from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from example_projects.pharmax.Backend.app.core.dependencies import require_role
from example_projects.pharmax.Backend.app.db.session import get_db
from example_projects.pharmax.Backend.app.models.user_table import UserRole
from example_projects.pharmax.Backend.app.schemas.user_schema import (
    CreateUserTask,
    CreateManagedUser,
    ResetUserPassword,
    ResetUserPin,
    UserActivityLogRead,
    UserTaskRead,
    UpdateUserRole,
    UpdateUserTaskStatus,
    UpdateUserStatus,
    UserRead,
    UserResetPinResponse,
)
from example_projects.pharmax.Backend.app.services.user_service import UserService


router = APIRouter()


@router.get("/", response_model=list[UserRead])
def list_users(
    search: str | None = Query(default=None),
    role: UserRole | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    limit: int = Query(default=200, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.ADMIN)),
):
    return UserService.list_users(db, search=search, role=role, is_active=is_active, limit=limit)


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: CreateManagedUser,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.ADMIN)),
):
    try:
        return UserService.create_managed_user(db, payload=payload, actor_user_id=current_user.id)
    except ValueError as exc:
        if str(exc) == "username or email taken":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered",
            ) from exc
        raise


@router.patch("/{user_id}/role", response_model=UserRead)
def update_user_role(
    user_id: str,
    payload: UpdateUserRole,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.ADMIN)),
):
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserService.update_user_role(db, user=user, role=payload.role, actor_user_id=current_user.id)


@router.patch("/{user_id}/status", response_model=UserRead)
def update_user_status(
    user_id: str,
    payload: UpdateUserStatus,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.ADMIN)),
):
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == current_user.id and payload.is_active is False:
        raise HTTPException(status_code=400, detail="You cannot deactivate your own account")

    return UserService.update_user_status(
        db,
        user=user,
        is_active=payload.is_active,
        actor_user_id=current_user.id,
    )


@router.post("/{user_id}/reset-password", response_model=UserRead)
def reset_user_password(
    user_id: str,
    payload: ResetUserPassword,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.ADMIN)),
):
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserService.reset_user_password(
        db,
        user=user,
        password=payload.password,
        actor_user_id=current_user.id,
    )


@router.post("/{user_id}/reset-pin", response_model=UserResetPinResponse)
def reset_user_pin(
    user_id: str,
    payload: ResetUserPin,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.ADMIN)),
):
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    UserService.reset_user_pin(
        db,
        user=user,
        pin=payload.pin,
        actor_user_id=current_user.id,
    )

    return {"message": "PIN updated"}


@router.get("/activity", response_model=list[UserActivityLogRead])
def list_user_activity(
    user_id: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.ADMIN)),
):
    return UserService.list_user_activity_logs(db, user_id=user_id, limit=limit)


@router.get("/tasks", response_model=list[UserTaskRead])
def list_user_tasks(
    assignee_user_id: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=300),
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.ADMIN)),
):
    return UserService.list_user_tasks(db, assignee_user_id=assignee_user_id, limit=limit)


@router.post("/tasks", response_model=UserTaskRead, status_code=status.HTTP_201_CREATED)
def assign_user_task(
    payload: CreateUserTask,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.ADMIN)),
):
    try:
        return UserService.create_user_task(
            db,
            actor_user_id=current_user.id,
            assignee_user_id=payload.assignee_user_id,
            title=payload.title,
            note=payload.note,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.patch("/tasks/{task_id}/status", response_model=UserTaskRead)
def update_user_task_status(
    task_id: str,
    payload: UpdateUserTaskStatus,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.ADMIN)),
):
    try:
        return UserService.update_user_task_status(
            db,
            task_id=task_id,
            actor_user_id=current_user.id,
            is_done=payload.is_done,
        )
    except ValueError as exc:
        if str(exc) == "task not found":
            raise HTTPException(status_code=404, detail="Task not found") from exc
        raise HTTPException(status_code=400, detail=str(exc)) from exc
