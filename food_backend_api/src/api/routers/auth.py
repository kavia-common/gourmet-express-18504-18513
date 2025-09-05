from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr, Field
from uuid import uuid4

from ..core.security import get_password_hash, verify_password, create_access_token, decode_access_token
from ..repositories.in_memory import InMemoryDB, UserRecord

router = APIRouter(tags=["Auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class RegisterRequest(BaseModel):
    email: EmailStr = Field(..., description="Email address of the user")
    password: str = Field(..., min_length=6, description="Password for the account")
    full_name: Optional[str] = Field(None, description="Full name of the user")


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Type of the token")


def get_user_by_email(email: str) -> Optional[UserRecord]:
    for u in InMemoryDB.users.values():
        if u.email.lower() == email.lower():
            return u
    return None


def authenticate_user(email: str, password: str) -> Optional[UserRecord]:
    user = get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


# PUBLIC_INTERFACE
@router.post("/register", response_model=TokenResponse, summary="Register a new user", description="Create a new user and return JWT.")
def register(payload: RegisterRequest):
    """Register a new user, store in-memory, and return an access token."""
    existing = get_user_by_email(payload.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user_id = str(uuid4())
    new_user = UserRecord(
        id=user_id,
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        full_name=payload.full_name,
    )
    InMemoryDB.users[user_id] = new_user
    token = create_access_token({"sub": user_id, "email": new_user.email})
    InMemoryDB.tokens_to_user[token] = user_id
    return TokenResponse(access_token=token)


# PUBLIC_INTERFACE
@router.post("/login", response_model=TokenResponse, summary="Login to get JWT", description="Authenticate using username/email and password to get JWT.")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint using OAuth2PasswordRequestForm (username as email)."""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token({"sub": user.id, "email": user.email})
    InMemoryDB.tokens_to_user[token] = user.id
    return TokenResponse(access_token=token)


def get_current_user(token: str = Depends(oauth2_scheme)) -> UserRecord:
    """Dependency to get the currently authenticated user via JWT token."""
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user_id = payload.get("sub")
    if not user_id or user_id not in InMemoryDB.users:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return InMemoryDB.users[user_id]


# PUBLIC_INTERFACE
@router.get("/me", summary="Get current user", description="Return current authenticated user details.")
def get_me(current_user: UserRecord = Depends(get_current_user)):
    """Return the currently authenticated user's basic info."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "phone": current_user.phone,
        "address": current_user.address,
    }
