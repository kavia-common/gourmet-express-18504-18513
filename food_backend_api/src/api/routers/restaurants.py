from typing import List, Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from ..repositories.in_memory import InMemoryDB

router = APIRouter(tags=["Restaurants"])


class Restaurant(BaseModel):
    id: str = Field(..., description="Restaurant ID")
    name: str = Field(..., description="Name")
    cuisine: str = Field(..., description="Cuisine type")
    rating: float = Field(..., description="Rating (0-5)")
    is_open: bool = Field(..., description="Open status")
    description: Optional[str] = Field(None, description="Description")


# PUBLIC_INTERFACE
@router.get("/", response_model=List[Restaurant], summary="List restaurants", description="Browse restaurants with optional name/cuisine search.")
def list_restaurants(q: Optional[str] = Query(None, description="Search term on name or cuisine")):
    """Return list of restaurants, filtered by optional search query."""
    all_r = list(InMemoryDB.restaurants.values())
    if q:
        q_lower = q.lower()
        all_r = [r for r in all_r if q_lower in r.name.lower() or q_lower in r.cuisine.lower()]
    return [Restaurant(**r.__dict__) for r in all_r]


# PUBLIC_INTERFACE
@router.get("/{restaurant_id}", response_model=Restaurant, summary="Get restaurant", description="Get details for a specific restaurant by ID.")
def get_restaurant(restaurant_id: str):
    """Get restaurant details by ID."""
    r = InMemoryDB.restaurants.get(restaurant_id)
    if not r:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")
    return Restaurant(**r.__dict__)
