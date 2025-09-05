from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from .auth import get_current_user
from ..repositories.in_memory import InMemoryDB, UserRecord

router = APIRouter(tags=["Notifications"])


class SubscriptionRequest(BaseModel):
    endpoint: str = Field(..., description="Notification endpoint or token (stub)")
    provider: str = Field(..., description="Provider name (e.g., 'fcm', 'sns', 'web')")


class NotifyRequest(BaseModel):
    title: str = Field(..., description="Notification title")
    body: str = Field(..., description="Notification body")
    order_id: Optional[str] = Field(None, description="Related order ID")


# PUBLIC_INTERFACE
@router.post("/subscribe", summary="Subscribe to notifications (stub)", description="Registers a notification endpoint for the user (stub only).")
def subscribe(payload: SubscriptionRequest, current_user: UserRecord = Depends(get_current_user)):
    """Store a simple in-memory mapping of user to 'subscription' (stub)."""
    subs = getattr(InMemoryDB, "subscriptions", {})
    subs[current_user.id] = {"endpoint": payload.endpoint, "provider": payload.provider}
    InMemoryDB.subscriptions = subs
    return {"message": "Subscribed", "user_id": current_user.id}


# PUBLIC_INTERFACE
@router.post("/send", summary="Send a notification (stub)", description="Pretend to send a push notification to the current user (stub).")
def send_notification(payload: NotifyRequest, current_user: UserRecord = Depends(get_current_user)):
    """Pretend to send a notification via previously registered channel."""
    subs = getattr(InMemoryDB, "subscriptions", {})
    sub = subs.get(current_user.id)
    delivered = sub is not None
    return {
        "delivered": delivered,
        "to": sub if sub else None,
        "title": payload.title,
        "body": payload.body,
        "order_id": payload.order_id,
    }
