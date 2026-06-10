from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from example_projects.pharmax.Backend.app.core.security import Token, create_access_token
from example_projects.pharmax.Backend.app.core.dependencies import get_current_user
from example_projects.pharmax.Backend.app.db.session import get_db
from example_projects.pharmax.Backend.app.models.user_table import User
from example_projects.pharmax.Backend.app.schemas.user_schema import LoginUser, PinLoginUser, RegisterRequestResponse, RegisterUser, UserRead
from example_projects.pharmax.Backend.app.services.user_service import UserService


router = APIRouter()


@router.post("/register", response_model=RegisterRequestResponse, status_code=status.HTTP_202_ACCEPTED)
def register(user: RegisterUser, db: Session = Depends(get_db)):
    try:
        created = UserService.register_user(db, user)
    except ValueError as exc:
        # Map our specific conflict signal to a 400; re-raise anything else
        if str(exc) == "username or email taken":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered") from exc
        if str(exc) == "no admin approver configured":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Registration queue is unavailable right now. Please contact admin directly.",
            ) from exc
        raise

    return created


@router.post("/token", response_model=Token)
def form_login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2PasswordRequestForm provides form-encoded username & password fields.
    # We treat `username` as our identifier (username or email).
    authenticated = UserService.authenticate(db, form_data.username, form_data.password)
    if not authenticated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid credentials",
        )

    access_token = create_access_token({"sub": authenticated.id, "role": authenticated.role.value})
    return Token(access_token=access_token, token_type="bearer")

@router.post("/login",response_model=Token)
def login(user: LoginUser, db: Session = Depends(get_db)):
    authenticated = UserService.authenticate(db, user.identifier,user.password)

    if not authenticated:
        if UserService.has_pending_password_login(db, user.identifier, user.password):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account pending admin approval. Please wait for activation.",
            )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid authentication credentials")
    
    access_token = create_access_token({"sub": authenticated.id, "role": authenticated.role.value})
    return Token(access_token=access_token, token_type="bearer")


@router.post("/pin-login", response_model=Token)
def pin_login(user: PinLoginUser, db: Session = Depends(get_db)):
    authenticated = UserService.authenticate_by_pin(db, user.identifier, user.pin)

    if not authenticated:
        if UserService.has_pending_pin_login(db, user.identifier, user.pin):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account pending admin approval. Please wait for activation.",
            )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid PIN or no PIN set for this account")

    access_token = create_access_token({"sub": authenticated.id, "role": authenticated.role.value})
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserRead)
def read_me(current_user = Depends(get_current_user)):
    return current_user


@router.post("/presence/heartbeat", response_model=UserRead)
def presence_heartbeat(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return UserService.touch_presence(db, current_user)


@router.post("/logout")
def logout(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    UserService.touch_presence(db, current_user, mark_logout=True)
    return {"message": "Logged out"}


@router.get("/ping")
def ping():
    return {"status": "ok"}
