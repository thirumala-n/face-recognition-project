from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.repositories import UserRepository
from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin, UserResponse, TokenResponse
from app.core.security import hash_password, verify_password, create_access_token
from app.api.deps import get_current_user
from app.core.logging_config import logger

router = APIRouter()

@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new system user"
)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    """
    Registers a new administrative or staff user.
    Validates unique email and unique username.
    Hashes password using bcrypt.
    Returns access token and user profile.
    """
    # Check duplicate email
    if UserRepository.get_by_email(db, payload.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"An account with email '{payload.email}' already exists."
        )

    # Check duplicate username
    if UserRepository.get_by_username(db, payload.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username '{payload.username}' is already taken."
        )

    # Hash password safely with bcrypt
    hashed = hash_password(payload.password)

    new_user = User(
        full_name=payload.full_name,
        email=payload.email.strip().lower(),
        username=payload.username.strip().lower(),
        password_hash=hashed,
        role="admin"
    )
    saved_user = UserRepository.create(db, new_user)
    logger.info(f"User registered: {saved_user.username} ({saved_user.email})")

    # Generate JWT token
    access_token = create_access_token(data={"sub": str(saved_user.id), "username": saved_user.username})

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(saved_user)
    )

@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate and receive JWT access token"
)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticates a user via email or username and plaintext password.
    Returns signed JWT access token upon successful verification.
    """
    user = UserRepository.get_by_email_or_username(db, payload.email_or_username)
    if not user:
        logger.warning(f"Failed login attempt for identifier: {payload.email_or_username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email/username or password.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not verify_password(payload.password, user.password_hash):
        logger.warning(f"Failed password verification for user ID: {user.id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email/username or password.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = create_access_token(data={"sub": str(user.id), "username": user.username})
    logger.info(f"User logged in successfully: {user.username} (ID: {user.id})")

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )

@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get currently authenticated user"
)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Returns the currently authenticated user's profile.
    Requires a valid JWT Bearer token in the Authorization header.
    """
    return UserResponse.model_validate(current_user)
