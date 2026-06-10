import logging
from datetime import datetime
from uuid import uuid4

from sqlalchemy import String, asc, cast, desc, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from example_projects.pharmax.Backend.app.core.security import get_password_hash, get_pin_hash, verify_password, verify_pin
from example_projects.pharmax.Backend.app.models.audit_log_table import AuditLog
from example_projects.pharmax.Backend.app.models.user_table import User, UserRole
from example_projects.pharmax.Backend.app.schemas.user_schema import CreateManagedUser, RegisterUser
from example_projects.pharmax.Backend.app.services.audit_service import AuditService


logger = logging.getLogger(__name__)


class UserService:
    """User-related business logic (registration, authentication)."""

    @staticmethod
    def register_user(db: Session, payload: RegisterUser) -> dict:
        """Create an inactive user and queue an admin approval task."""

        stmt = select(User).where(
            or_(User.username == payload.username, User.email == payload.email)
        )
        existing = db.execute(stmt).scalars().first()

        if existing:
            # Let the route decide exact HTTP response; here we just signal conflict
            raise ValueError("username or email taken")

        admin_candidates = db.execute(
            select(User).where(User.role == UserRole.ADMIN).order_by(User.created_at.asc())
        ).scalars().all()
        approver = next((candidate for candidate in admin_candidates if candidate.is_active), None)
        if approver is None and admin_candidates:
            approver = admin_candidates[0]

        if approver is None:
            raise ValueError("no admin approver configured")

        user = User(
            username=payload.username,
            email=payload.email,
            full_name=payload.full_name,
            role=payload.role,
            hashed_password=get_password_hash(payload.password),
            is_active=False,
        )

        db.add(user)
        db.flush()

        request_id = str(uuid4())
        title = f"Approve registration: {user.username}"
        note = (
            f"{user.full_name or user.username} requested {user.role.value} access. "
            f"Email: {user.email}. Review the account and activate if approved."
        )

        AuditService.log_action(
            db=db,
            user_id=approver.id,
            action="ASSIGN_TASK",
            resource_type="USER_TASK",
            resource_id=request_id,
            details={
                "task_id": request_id,
                "title": title,
                "note": note,
                "assignee_user_id": approver.id,
                "created_by_user_id": approver.id,
                "is_done": False,
                "request_source": "PUBLIC_REGISTER",
                "requested_user_id": user.id,
                "requested_username": user.username,
                "requested_email": user.email,
                "requested_role": user.role.value,
            },
        )

        AuditService.log_action(
            db=db,
            user_id=approver.id,
            action="REGISTER_REQUEST",
            resource_type="USER",
            resource_id=user.id,
            details={
                "username": user.username,
                "email": user.email,
                "role": user.role.value,
                "is_active": user.is_active,
                "approval_task_id": request_id,
            },
        )
        db.commit()
        db.refresh(user)
        return {
            "message": "Request sent to admin. Your account will be activated after approval.",
            "request_id": request_id,
        }

    @staticmethod
    def authenticate(db: Session, identifier: str, password: str) -> User | None:
        """Return user if identifier (username or email) + password are valid."""

        identifier = (identifier or "").strip()
        if not identifier or not password:
            return None

        stmt = select(User).where(
            or_(User.username == identifier, User.email == identifier)
        )
        try:
            users = db.execute(stmt).scalars().all()
        except SQLAlchemyError:
            logger.exception("Auth query failed for identifier '%s'", identifier)
            return None

        if not users:
            return None

        user = next((u for u in users if u.is_active), users[0])

        try:
            if not verify_password(password, user.hashed_password):
                return None
        except (TypeError, ValueError):
            logger.warning("Password hash verification failed for user '%s'", user.username)
            return None

        if not user.is_active:
            return None

        user_id = user.id
        username = user.username
        role_value = user.role.value
        now = datetime.utcnow()
        user.last_login_at = now
        user.last_seen_at = now
        user.last_logout_at = None

        try:
            db.commit()
            db.refresh(user)
        except SQLAlchemyError:
            db.rollback()
            logger.warning("Login timestamp update failed for user '%s'", username)

        try:
            AuditService.log_action(
                db=db,
                user_id=user_id,
                action="LOGIN",
                resource_type="USER",
                resource_id=user_id,
                details={"identifier": identifier, "role": role_value},
            )
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            logger.warning("Audit logging failed during LOGIN for user '%s'", username)

        refreshed = db.get(User, user_id)
        return refreshed if refreshed and refreshed.is_active else None

    @staticmethod
    def has_pending_password_login(db: Session, identifier: str, password: str) -> bool:
        """True when credentials are correct but account is inactive (awaiting approval)."""

        identifier = (identifier or "").strip()
        if not identifier or not password:
            return False

        stmt = select(User).where(or_(User.username == identifier, User.email == identifier))
        try:
            users = db.execute(stmt).scalars().all()
        except SQLAlchemyError:
            return False

        for user in users:
            if user.is_active:
                continue
            try:
                if verify_password(password, user.hashed_password):
                    return True
            except (TypeError, ValueError):
                continue
        return False

    @staticmethod
    def authenticate_by_pin(db: Session, identifier: str, pin: str) -> User | None:
        """Return user if identifier (username or email) + PIN are valid."""

        identifier = (identifier or "").strip()
        if not identifier or not pin:
            return None

        stmt = select(User).where(
            or_(User.username == identifier, User.email == identifier)
        )
        try:
            users = db.execute(stmt).scalars().all()
        except SQLAlchemyError:
            logger.exception("PIN auth query failed for identifier '%s'", identifier)
            return None

        if not users:
            return None

        user = next((u for u in users if u.is_active), users[0])

        if not user.hashed_pin:
            return None

        try:
            if not verify_pin(pin, user.hashed_pin):
                return None
        except (TypeError, ValueError):
            logger.warning("PIN hash verification failed for user '%s'", user.username)
            return None

        if not user.is_active:
            return None

        user_id = user.id
        username = user.username
        role_value = user.role.value
        now = datetime.utcnow()
        user.last_login_at = now
        user.last_seen_at = now
        user.last_logout_at = None

        try:
            db.commit()
            db.refresh(user)
        except SQLAlchemyError:
            db.rollback()
            logger.warning("PIN login timestamp update failed for user '%s'", username)

        try:
            AuditService.log_action(
                db=db,
                user_id=user_id,
                action="PIN_LOGIN",
                resource_type="USER",
                resource_id=user_id,
                details={"identifier": identifier, "role": role_value},
            )
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            logger.warning("Audit logging failed during PIN_LOGIN for user '%s'", username)

        refreshed = db.get(User, user_id)
        return refreshed if refreshed and refreshed.is_active else None

    @staticmethod
    def has_pending_pin_login(db: Session, identifier: str, pin: str) -> bool:
        """True when PIN is correct but account is inactive (awaiting approval)."""

        identifier = (identifier or "").strip()
        if not identifier or not pin:
            return False

        stmt = select(User).where(or_(User.username == identifier, User.email == identifier))
        try:
            users = db.execute(stmt).scalars().all()
        except SQLAlchemyError:
            return False

        for user in users:
            if user.is_active or not user.hashed_pin:
                continue
            try:
                if verify_pin(pin, user.hashed_pin):
                    return True
            except (TypeError, ValueError):
                continue
        return False

    @staticmethod
    def touch_presence(
        db: Session,
        user: User,
        *,
        mark_logout: bool = False,
    ) -> User:
        now = datetime.utcnow()
        user.last_seen_at = now
        if mark_logout:
            user.last_logout_at = now

        if mark_logout:
            AuditService.log_action(
                db=db,
                user_id=user.id,
                action="LOGOUT",
                resource_type="USER",
                resource_id=user.id,
                details={"username": user.username},
            )

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def _serialize_audit_logs(logs: list[AuditLog]) -> list[dict]:
        return [
            {
                "id": log.id,
                "created_at": log.created_at,
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "actor_user_id": log.user_id,
                "actor_username": log.user.username if log.user else None,
                "actor_full_name": log.user.full_name if log.user else None,
                "details": log.details_dict,
            }
            for log in logs
        ]

    @staticmethod
    def _matches_period(timestamp: datetime | None, period: str) -> bool:
        if timestamp is None:
            return False

        hour = int(timestamp.hour)
        if period == "morning":
            return 5 <= hour < 12
        if period == "afternoon":
            return 12 <= hour < 17
        if period == "evening":
            return 17 <= hour < 21
        if period == "night":
            return hour >= 21 or hour < 5
        return True

    @staticmethod
    def list_activity_logs(
        db: Session,
        *,
        current_user: User,
        limit: int = 120,
        action: str | None = None,
        resource_type: str | None = None,
        actor_user_id: str | None = None,
        search: str | None = None,
        from_at: datetime | None = None,
        to_at: datetime | None = None,
        period: str = "all",
        sort: str = "desc",
    ) -> list[dict]:
        normalized_period = str(period or "all").strip().lower()
        normalized_sort = str(sort or "desc").strip().lower()

        stmt = select(AuditLog)

        if current_user.role == UserRole.STAFF:
            stmt = stmt.where(AuditLog.user_id == current_user.id)
        elif actor_user_id:
            stmt = stmt.where(AuditLog.user_id == actor_user_id)

        if action:
            stmt = stmt.where(AuditLog.action == str(action).strip().upper())

        if resource_type:
            stmt = stmt.where(AuditLog.resource_type == str(resource_type).strip().upper())

        if from_at:
            stmt = stmt.where(AuditLog.created_at >= from_at)

        if to_at:
            stmt = stmt.where(AuditLog.created_at <= to_at)

        normalized_search = str(search or "").strip()
        if normalized_search:
            like = f"%{normalized_search}%"
            stmt = stmt.where(
                or_(
                    AuditLog.action.ilike(like),
                    AuditLog.resource_type.ilike(like),
                    AuditLog.resource_id.ilike(like),
                    cast(AuditLog.details, String).ilike(like),
                )
            )

        order_clause = asc(AuditLog.created_at) if normalized_sort == "asc" else desc(AuditLog.created_at)
        scan_limit = max(int(limit or 1) * 6, 240)
        logs = db.execute(stmt.order_by(order_clause).limit(scan_limit)).scalars().all()

        if normalized_period != "all":
            logs = [log for log in logs if UserService._matches_period(log.created_at, normalized_period)]

        return UserService._serialize_audit_logs(logs[:limit])

    @staticmethod
    def list_users(
        db: Session,
        *,
        search: str | None = None,
        role: UserRole | None = None,
        is_active: bool | None = None,
        limit: int = 200,
    ) -> list[User]:
        stmt = select(User)

        normalized_search = (search or "").strip()
        if normalized_search:
            like = f"%{normalized_search}%"
            stmt = stmt.where(
                or_(
                    User.username.ilike(like),
                    User.email.ilike(like),
                    User.full_name.ilike(like),
                )
            )

        if role:
            stmt = stmt.where(User.role == role)

        if is_active is not None:
            stmt = stmt.where(User.is_active == is_active)

        stmt = stmt.order_by(User.created_at.desc()).limit(limit)
        return db.execute(stmt).scalars().all()

    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> User | None:
        return db.get(User, user_id)

    @staticmethod
    def create_managed_user(db: Session, payload: CreateManagedUser, actor_user_id: str) -> User:
        stmt = select(User).where(
            or_(User.username == payload.username, User.email == payload.email)
        )
        existing = db.execute(stmt).scalars().first()
        if existing:
            raise ValueError("username or email taken")

        user = User(
            username=payload.username,
            email=payload.email,
            full_name=payload.full_name,
            role=payload.role,
            hashed_password=get_password_hash(payload.password),
            hashed_pin=get_pin_hash(payload.pin) if payload.pin else None,
            is_active=True,
        )

        db.add(user)
        db.flush()

        AuditService.log_action(
            db=db,
            user_id=actor_user_id,
            action="CREATE_MANAGED_USER",
            resource_type="USER",
            resource_id=user.id,
            details={
                "created_user": user.username,
                "created_role": user.role.value,
                "has_pin": bool(payload.pin),
            },
        )
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def update_user_role(db: Session, user: User, role: UserRole, actor_user_id: str) -> User:
        old_role = user.role.value
        user.role = role

        AuditService.log_action(
            db=db,
            user_id=actor_user_id,
            action="UPDATE_ROLE",
            resource_type="USER",
            resource_id=user.id,
            details={"from": old_role, "to": role.value},
        )
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def list_user_activity_logs(
        db: Session,
        *,
        user_id: str | None = None,
        limit: int = 50,
    ) -> list[dict]:
        stmt = (
            select(AuditLog)
            .where(AuditLog.resource_type.in_(["USER", "User", "USER_TASK"]))
            .order_by(desc(AuditLog.created_at))
            .limit(limit)
        )

        if user_id:
            stmt = (
                select(AuditLog)
                .where(
                    AuditLog.resource_type.in_(["USER", "User", "USER_TASK"]),
                    or_(AuditLog.resource_id == user_id, AuditLog.user_id == user_id),
                )
                .order_by(desc(AuditLog.created_at))
                .limit(limit)
            )

        logs = db.execute(stmt).scalars().all()
        return UserService._serialize_audit_logs(logs)

    @staticmethod
    def create_user_task(
        db: Session,
        *,
        actor_user_id: str,
        assignee_user_id: str,
        title: str,
        note: str,
    ) -> dict:
        assignee = db.get(User, assignee_user_id)
        if not assignee:
            raise ValueError("assignee not found")

        task_id = str(uuid4())
        AuditService.log_action(
            db=db,
            user_id=actor_user_id,
            action="ASSIGN_TASK",
            resource_type="USER_TASK",
            resource_id=task_id,
            details={
                "task_id": task_id,
                "title": title,
                "note": note,
                "assignee_user_id": assignee_user_id,
                "created_by_user_id": actor_user_id,
                "is_done": False,
            },
        )
        db.commit()

        tasks = UserService.list_user_tasks(db, assignee_user_id=assignee_user_id, limit=200)
        return next((task for task in tasks if task["id"] == task_id), {
            "id": task_id,
            "title": title,
            "note": note,
            "assignee_user_id": assignee_user_id,
            "assignee_username": assignee.username,
            "assignee_full_name": assignee.full_name,
            "created_by_user_id": actor_user_id,
            "created_by_username": None,
            "created_by_full_name": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_done": False,
        })

    @staticmethod
    def update_user_task_status(
        db: Session,
        *,
        task_id: str,
        actor_user_id: str,
        is_done: bool,
    ) -> dict:
        existing_tasks = UserService.list_user_tasks(db, limit=400)
        target = next((task for task in existing_tasks if task["id"] == task_id), None)
        if not target:
            raise ValueError("task not found")

        AuditService.log_action(
            db=db,
            user_id=actor_user_id,
            action="TASK_STATUS",
            resource_type="USER_TASK",
            resource_id=task_id,
            details={
                "task_id": task_id,
                "is_done": bool(is_done),
                "assignee_user_id": target.get("assignee_user_id"),
                "title": target.get("title"),
                "note": target.get("note"),
            },
        )
        db.commit()

        updated_tasks = UserService.list_user_tasks(db, limit=400)
        updated = next((task for task in updated_tasks if task["id"] == task_id), None)
        if not updated:
            raise ValueError("task not found")
        return updated

    @staticmethod
    def list_user_tasks(
        db: Session,
        *,
        assignee_user_id: str | None = None,
        limit: int = 100,
    ) -> list[dict]:
        scan_limit = max(limit, 1) * 8
        stmt = (
            select(AuditLog)
            .where(AuditLog.resource_type == "USER_TASK")
            .order_by(desc(AuditLog.created_at))
            .limit(scan_limit)
        )
        logs = db.execute(stmt).scalars().all()

        tasks: dict[str, dict] = {}

        for log in reversed(logs):
            details = log.details_dict
            task_id = log.resource_id or details.get("task_id")
            if not task_id:
                continue

            task = tasks.get(task_id)
            if task is None:
                task = {
                    "id": task_id,
                    "title": str(details.get("title") or "Team task").strip() or "Team task",
                    "note": str(details.get("note") or "").strip(),
                    "assignee_user_id": details.get("assignee_user_id"),
                    "created_by_user_id": details.get("created_by_user_id") or log.user_id,
                    "created_at": log.created_at,
                    "updated_at": log.created_at,
                    "is_done": bool(details.get("is_done", False)),
                }
                tasks[task_id] = task

            task["updated_at"] = log.created_at

            if log.action == "ASSIGN_TASK":
                task["title"] = str(details.get("title") or task["title"]).strip() or task["title"]
                task["note"] = str(details.get("note") or task["note"]).strip()
                task["assignee_user_id"] = details.get("assignee_user_id") or task.get("assignee_user_id")
                task["created_by_user_id"] = details.get("created_by_user_id") or task.get("created_by_user_id")
                task["is_done"] = bool(details.get("is_done", False))
            elif log.action == "TASK_STATUS":
                task["is_done"] = bool(details.get("is_done", task["is_done"]))

        user_ids = {
            t["assignee_user_id"] for t in tasks.values() if t.get("assignee_user_id")
        } | {
            t["created_by_user_id"] for t in tasks.values() if t.get("created_by_user_id")
        }

        user_lookup: dict[str, User] = {}
        if user_ids:
            users = db.execute(select(User).where(User.id.in_(user_ids))).scalars().all()
            user_lookup = {user.id: user for user in users}

        result = []
        for task in tasks.values():
            assignee = user_lookup.get(task.get("assignee_user_id"))
            creator = user_lookup.get(task.get("created_by_user_id"))
            item = {
                **task,
                "assignee_username": assignee.username if assignee else None,
                "assignee_full_name": assignee.full_name if assignee else None,
                "created_by_username": creator.username if creator else None,
                "created_by_full_name": creator.full_name if creator else None,
            }
            result.append(item)

        if assignee_user_id:
            result = [task for task in result if task.get("assignee_user_id") == assignee_user_id]

        result.sort(key=lambda task: task.get("updated_at") or datetime.min, reverse=True)
        result.sort(key=lambda task: task.get("is_done", False))
        return result[:limit]

    @staticmethod
    def update_user_status(db: Session, user: User, is_active: bool, actor_user_id: str) -> User:
        user.is_active = is_active
        AuditService.log_action(
            db=db,
            user_id=actor_user_id,
            action="UPDATE_STATUS",
            resource_type="USER",
            resource_id=user.id,
            details={"is_active": is_active},
        )
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def reset_user_password(db: Session, user: User, password: str, actor_user_id: str) -> User:
        user.hashed_password = get_password_hash(password)
        AuditService.log_action(
            db=db,
            user_id=actor_user_id,
            action="RESET_PASSWORD",
            resource_type="USER",
            resource_id=user.id,
            details={"target_user": user.username},
        )
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def reset_user_pin(db: Session, user: User, pin: str, actor_user_id: str) -> User:
        user.hashed_pin = get_pin_hash(pin)
        AuditService.log_action(
            db=db,
            user_id=actor_user_id,
            action="RESET_PIN",
            resource_type="USER",
            resource_id=user.id,
            details={"target_user": user.username},
        )
        db.commit()
        db.refresh(user)
        return user
