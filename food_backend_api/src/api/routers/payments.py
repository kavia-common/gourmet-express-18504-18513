from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from ..repositories.in_memory import InMemoryDB
from .auth import get_current_user
from ..repositories.in_memory import UserRecord

router = APIRouter(tags=["Payments"])


class PaymentInitiateRequest(BaseModel):
    order_id: str = Field(..., description="Order ID to pay for")
    method: Literal["card", "wallet", "cod"] = Field(..., description="Payment method")


class PaymentInitiateResponse(BaseModel):
    payment_id: str = Field(..., description="Mock payment ID")
    status: Literal["requires_action", "succeeded"] = Field(..., description="Mock payment status")
    client_secret: str | None = Field(None, description="Client secret for additional steps, if any")


class PaymentVerifyRequest(BaseModel):
    payment_id: str = Field(..., description="Mock payment ID returned earlier")


# PUBLIC_INTERFACE
@router.post("/initiate", response_model=PaymentInitiateResponse, summary="Initiate payment (mock)", description="Start a mocked payment process for an order.")
def initiate_payment(payload: PaymentInitiateRequest, current_user: UserRecord = Depends(get_current_user)):
    """Mock payment initiation: validates order and returns a fake payment object."""
    order = InMemoryDB.orders.get(payload.order_id)
    if not order or order.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    # For card/wallet, assume requires_action; for cod, succeeded immediately
    if payload.method in ("card", "wallet"):
        payment_id = f"pay_{payload.order_id}"
        return PaymentInitiateResponse(payment_id=payment_id, status="requires_action", client_secret="mock_client_secret")
    else:
        order.status = "paid"
        InMemoryDB.orders[payload.order_id] = order
        payment_id = f"pay_{payload.order_id}"
        return PaymentInitiateResponse(payment_id=payment_id, status="succeeded", client_secret=None)


# PUBLIC_INTERFACE
@router.post("/verify", summary="Verify payment (mock)", description="Complete a mocked payment flow by verifying client action.")
def verify_payment(payload: PaymentVerifyRequest, current_user: UserRecord = Depends(get_current_user)):
    """Mock payment verification: marks order as paid if payment_id matches known format."""
    if not payload.payment_id.startswith("pay_"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payment id")
    order_id = payload.payment_id.split("pay_")[-1]
    order = InMemoryDB.orders.get(order_id)
    if not order or order.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    order.status = "paid"
    InMemoryDB.orders[order_id] = order
    return {"message": "Payment verified", "order_id": order_id, "status": "paid"}
