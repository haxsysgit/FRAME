from pydantic import BaseModel, constr
from example_projects.pharmax.Backend.app.models.user_table import UserRole
from datetime import datetime

class UserBase(BaseModel):
    username: constr(max_length=72)
    email: constr(max_length=72)
    full_name: str | None = None
    role: UserRole


class RegisterUser(UserBase):
    password: constr(min_length=8, max_length=72)


class RegisterRequestResponse(BaseModel):
    message: str
    request_id: str


class CreateManagedUser(RegisterUser):
    pin: constr(min_length=4, max_length=6) | None = None


class UpdateUserRole(BaseModel):
    role: UserRole


class UpdateUserStatus(BaseModel):
    is_active: bool


class ResetUserPassword(BaseModel):
    password: constr(min_length=8, max_length=72)


class ResetUserPin(BaseModel):
    pin: constr(min_length=4, max_length=6)


class UserResetPinResponse(BaseModel):
    message: str


class UserActivityLogRead(BaseModel):
    id: str
    created_at: datetime
    action: str
    resource_type: str
    resource_id: str | None = None
    actor_user_id: str
    actor_username: str | None = None
    actor_full_name: str | None = None
    details: dict | None = None


class CreateUserTask(BaseModel):
    assignee_user_id: str
    title: constr(min_length=3, max_length=120)
    note: constr(min_length=1, max_length=500)


class UpdateUserTaskStatus(BaseModel):
    is_done: bool


class UserTaskRead(BaseModel):
    id: str
    title: str
    note: str
    assignee_user_id: str
    assignee_username: str | None = None
    assignee_full_name: str | None = None
    created_by_user_id: str
    created_by_username: str | None = None
    created_by_full_name: str | None = None
    created_at: datetime
    updated_at: datetime
    is_done: bool = False

class LoginUser(BaseModel):
    identifier: constr(max_length=72)
    password: constr(min_length=8, max_length=72)

class PinLoginUser(BaseModel):
    identifier: constr(max_length=72)
    pin: constr(min_length=4, max_length=6)

class UserRead(UserBase):
    model_config = {"from_attributes": True}

    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: datetime | None = None
    last_seen_at: datetime | None = None
    last_logout_at: datetime | None = None
    is_online: bool = False


