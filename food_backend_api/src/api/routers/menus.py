from typing import List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from ..repositories.in_memory import InMemoryDB

router = APIRouter(tags=["Menus"])


class MenuItem(BaseModel):
    id: str = Field(..., description="Menu item ID")
    restaurant_id: str = Field(..., description="Restaurant ID")
    name: str = Field(..., description="Item name")
    price: float = Field(..., description="Price")
    description: str | None = Field(None, description="Description")
    available: bool = Field(..., description="Availability")


# PUBLIC_INTERFACE
@router.get("/restaurant/{restaurant_id}", response_model=List[MenuItem], summary="List menu items", description="List all available menu items for a restaurant.")
def list_menu_items(restaurant_id: str):
    """List all menu items for a given restaurant."""
    items = [it for it in InMemoryDB.menu_items.values() if it.restaurant_id == restaurant_id and it.available]
    return [MenuItem(**it.__dict__) for it in items]


# PUBLIC_INTERFACE
@router.get("/{item_id}", response_model=MenuItem, summary="Get menu item", description="Get details for a specific menu item.")
def get_menu_item(item_id: str):
    """Get menu item details by ID."""
    it = InMemoryDB.menu_items.get(item_id)
    if not it:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")
    return MenuItem(**it.__dict__)
