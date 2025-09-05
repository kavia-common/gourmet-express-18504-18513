from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from ..repositories.in_memory import InMemoryDB, UserRecord
from .auth import get_current_user

router = APIRouter(tags=["Profiles"])


class ProfileResponse(BaseModel):
    id: str = Field(..., description="User ID")
    email: str = Field(..., description="Email address")
    full_name: Optional[str] = Field(None, description="Full name")
    phone: Optional[str] = Field(None, description="Phone number")
    address: Optional[str] = Field(None, description="Address")


class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(None, description="Full name")
    phone: Optional[str] = Field(None, description="Phone number")
    address: Optional[str] = Field(None, description="Address")


# PUBLIC_INTERFACE
@router.get("/me", response_model=ProfileResponse, summary="Get my profile", description="Fetch the authenticated user's profile.")
def get_profile(current_user: UserRecord = Depends(get_current_user)):
    """Return the current user's profile."""
    return ProfileResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        phone=current_user.phone,
        address=current_user.address,
    )


# PUBLIC_INTERFACE
@router.put("/me", response_model=ProfileResponse, summary="Update my profile", description="Update the authenticated user's profile fields.")
def update_profile(payload: ProfileUpdateRequest, current_user: UserRecord = Depends(get_current_user)):
    """Update fields on the user's in-memory profile."""
    if payload.full_name is not None:
        current_user.full_name = payload.full_name
    if payload.phone is not None:
        current_user.phone = payload.phone
    if payload.address is not None:
        current_user.address = payload.address
    InMemoryDB.users[current_user.id] = current_user
    return ProfileResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        phone=current_user.phone,
        address=current_user.address,
    )
