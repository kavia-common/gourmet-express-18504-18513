from typing import List
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from ..repositories.in_memory import InMemoryDB, OrderRecord, OrderItem
from .auth import get_current_user
from ..repositories.in_memory import UserRecord

router = APIRouter(tags=["Orders"])


class OrderItemRequest(BaseModel):
    item_id: str = Field(..., description="Menu item ID")
    quantity: int = Field(..., ge=1, description="Quantity >= 1")


class OrderCreateRequest(BaseModel):
    restaurant_id: str = Field(..., description="Restaurant ID")
    items: List[OrderItemRequest] = Field(..., description="List of items to order")


class OrderResponse(BaseModel):
    id: str = Field(..., description="Order ID")
    user_id: str = Field(..., description="User ID")
    restaurant_id: str = Field(..., description="Restaurant ID")
    items: List[OrderItemRequest] = Field(..., description="Ordered items")
    status: str = Field(..., description="Order status")
    total_amount: float = Field(..., description="Total order amount")
    eta_minutes: int = Field(..., description="Estimated time remaining in minutes")
    tracking_note: str = Field(..., description="Latest tracking message")


def _calculate_total(restaurant_id: str, items: List[OrderItemRequest]) -> float:
    total = 0.0
    for it in items:
        menu_item = InMemoryDB.menu_items.get(it.item_id)
        if not menu_item or menu_item.restaurant_id != restaurant_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid item {it.item_id}")
        total += menu_item.price * it.quantity
    return round(total, 2)


# PUBLIC_INTERFACE
@router.post("/", response_model=OrderResponse, summary="Place an order", description="Create a new order for the authenticated user.")
def place_order(payload: OrderCreateRequest, current_user: UserRecord = Depends(get_current_user)):
    """Create a new order and compute total; order starts in 'created' status."""
    if payload.restaurant_id not in InMemoryDB.restaurants:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")

    total = _calculate_total(payload.restaurant_id, payload.items)

    order_id = str(uuid4())
    order = OrderRecord(
        id=order_id,
        user_id=current_user.id,
        restaurant_id=payload.restaurant_id,
        items=[OrderItem(item_id=it.item_id, quantity=it.quantity) for it in payload.items],
        total_amount=total,
        status="created",
        tracking_note="Order created",
        eta_minutes=30,
    )
    InMemoryDB.orders[order_id] = order
    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        restaurant_id=order.restaurant_id,
        items=[OrderItemRequest(item_id=i.item_id, quantity=i.quantity) for i in order.items],
        status=order.status,
        total_amount=order.total_amount,
        eta_minutes=order.eta_minutes,
        tracking_note=order.tracking_note,
    )


# PUBLIC_INTERFACE
@router.get("/", response_model=List[OrderResponse], summary="List my orders", description="List orders for the authenticated user.")
def list_my_orders(current_user: UserRecord = Depends(get_current_user)):
    """Return orders belonging to current user."""
    res: List[OrderResponse] = []
    for order in InMemoryDB.orders.values():
        if order.user_id == current_user.id:
            res.append(
                OrderResponse(
                    id=order.id,
                    user_id=order.user_id,
                    restaurant_id=order.restaurant_id,
                    items=[OrderItemRequest(item_id=i.item_id, quantity=i.quantity) for i in order.items],
                    status=order.status,
                    total_amount=order.total_amount,
                    eta_minutes=order.eta_minutes,
                    tracking_note=order.tracking_note,
                )
            )
    return res


# PUBLIC_INTERFACE
@router.get("/{order_id}", response_model=OrderResponse, summary="Get order", description="Get an order by ID, only if it belongs to the authenticated user.")
def get_order(order_id: str, current_user: UserRecord = Depends(get_current_user)):
    """Retrieve a single order by ID."""
    order = InMemoryDB.orders.get(order_id)
    if not order or order.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        restaurant_id=order.restaurant_id,
        items=[OrderItemRequest(item_id=i.item_id, quantity=i.quantity) for i in order.items],
        status=order.status,
        total_amount=order.total_amount,
        eta_minutes=order.eta_minutes,
        tracking_note=order.tracking_note,
    )


# PUBLIC_INTERFACE
@router.get("/{order_id}/status", summary="Order status", description="Get current status of an order.")
def get_order_status(order_id: str, current_user: UserRecord = Depends(get_current_user)):
    """Return only the status field for a given order."""
    order = InMemoryDB.orders.get(order_id)
    if not order or order.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return {"id": order.id, "status": order.status, "eta_minutes": order.eta_minutes}


# PUBLIC_INTERFACE
@router.get("/{order_id}/track", summary="Track order (long-poll stub)", description="Stubbed tracking endpoint for clients to poll periodically.")
def track_order(order_id: str, current_user: UserRecord = Depends(get_current_user), step: int = Query(0, ge=0, description="Client-provided step to simulate tracking progression")):
    """
    Simulate order tracking via long-polling. Each step advances the tracking message and ETA.
    This is a stub and does not hold the connection open; clients can poll periodically.
    """
    order = InMemoryDB.orders.get(order_id)
    if not order or order.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    steps = [
        ("created", "Order created"),
        ("confirmed", "Restaurant confirmed your order"),
        ("preparing", "Your food is being prepared"),
        ("picked_up", "Courier picked up your order"),
        ("delivered", "Order delivered"),
    ]
    idx = min(step, len(steps) - 1)
    status_val, note = steps[idx]
    order.status = status_val
    order.tracking_note = note
    order.eta_minutes = max(0, order.eta_minutes - (5 if step > 0 else 0))
    InMemoryDB.orders[order_id] = order
    return {"id": order.id, "status": order.status, "tracking_note": order.tracking_note, "eta_minutes": order.eta_minutes}
