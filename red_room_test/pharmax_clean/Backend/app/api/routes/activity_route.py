from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from example_projects.pharmax.Backend.app.core.dependencies import require_role
from example_projects.pharmax.Backend.app.db.session import get_db
from example_projects.pharmax.Backend.app.models.user_table import User, UserRole
from example_projects.pharmax.Backend.app.schemas.user_schema import UserActivityLogRead
from example_projects.pharmax.Backend.app.services.user_service import UserService


router = APIRouter()


@router.get("/", response_model=list[UserActivityLogRead])
def list_activity_logs(
    limit: int = Query(default=180, ge=1, le=500),
    action: str | None = Query(default=None),
    resource_type: str | None = Query(default=None),
    actor_user_id: str | None = Query(default=None),
    search: str | None = Query(default=None),
    from_at: datetime | None = Query(default=None),
    to_at: datetime | None = Query(default=None),
    period: str = Query(default="all", pattern="^(all|morning|afternoon|evening|night)$"),
    sort: str = Query(default="desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.CASHIER, UserRole.STAFF)),
):
    return UserService.list_activity_logs(
        db,
        current_user=current_user,
        limit=limit,
        action=action,
        resource_type=resource_type,
        actor_user_id=actor_user_id,
        search=search,
        from_at=from_at,
        to_at=to_at,
        period=period,
        sort=sort,
    )
