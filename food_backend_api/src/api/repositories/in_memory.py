from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List
from datetime import datetime


@dataclass
class UserRecord:
    id: str
    email: str
    hashed_password: str
    full_name: str | None = None
    phone: str | None = None
    address: str | None = None


@dataclass
class RestaurantRecord:
    id: str
    name: str
    cuisine: str
    rating: float = 4.5
    is_open: bool = True
    description: str | None = None


@dataclass
class MenuItemRecord:
    id: str
    restaurant_id: str
    name: str
    price: float
    description: str | None = None
    available: bool = True


@dataclass
class OrderItem:
    item_id: str
    quantity: int


@dataclass
class OrderRecord:
    id: str
    user_id: str
    restaurant_id: str
    items: List[OrderItem]
    status: str = "created"
    total_amount: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    eta_minutes: int = 30
    tracking_note: str = "Order received"


class InMemoryDB:
    """Simple in-memory storage. Replace with real DB integration later."""
    users: Dict[str, UserRecord] = {}
    restaurants: Dict[str, RestaurantRecord] = {}
    menu_items: Dict[str, MenuItemRecord] = {}
    orders: Dict[str, OrderRecord] = {}
    tokens_to_user: Dict[str, str] = {}  # token -> user_id mapping (for stub validation)


# Seed with some restaurants and menu items for demo
def seed_data():
    r1 = RestaurantRecord(id="r_1", name="Pasta Palace", cuisine="Italian", rating=4.7)
    r2 = RestaurantRecord(id="r_2", name="Sushi Central", cuisine="Japanese", rating=4.6)
    r3 = RestaurantRecord(id="r_3", name="Spice Route", cuisine="Indian", rating=4.5)
    InMemoryDB.restaurants[r1.id] = r1
    InMemoryDB.restaurants[r2.id] = r2
    InMemoryDB.restaurants[r3.id] = r3

    items = [
        MenuItemRecord(id="m_1", restaurant_id="r_1", name="Spaghetti Carbonara", price=12.5),
        MenuItemRecord(id="m_2", restaurant_id="r_1", name="Margherita Pizza", price=10.0),
        MenuItemRecord(id="m_3", restaurant_id="r_2", name="Salmon Nigiri", price=8.0),
        MenuItemRecord(id="m_4", restaurant_id="r_2", name="California Roll", price=7.5),
        MenuItemRecord(id="m_5", restaurant_id="r_3", name="Butter Chicken", price=13.0),
        MenuItemRecord(id="m_6", restaurant_id="r_3", name="Paneer Tikka", price=11.0),
    ]
    for it in items:
        InMemoryDB.menu_items[it.id] = it


# Run seed at module import
seed_data()
