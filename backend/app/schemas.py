from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date


class CircularItemBase(BaseModel):
    retailer: str
    item_name: str
    price: Optional[float] = None
    regular_price: Optional[float] = None
    discount_percent: Optional[float] = None
    unit: str = "ea"
    category: Optional[str] = None
    source: str = "pdf"
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None


class CircularItemCreate(CircularItemBase):
    pass


class CircularItem(CircularItemBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class CircularItemResponse(BaseModel):
    id: int
    retailer: str
    item_name: str
    price: Optional[float] = None
    regular_price: Optional[float] = None
    discount_percent: Optional[float] = None
    unit: str
    category: Optional[str] = None
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None


class MemberBase(BaseModel):
    name: str
    role: Optional[str] = 'adult'
    age: Optional[int] = None
    allergies: Optional[str] = None
    dislikes: Optional[str] = None
    likes: Optional[str] = None
    favorite_recipes: Optional[str] = None
    dietary_pref: Optional[str] = None


class MemberCreate(MemberBase):
    pass


class Member(MemberBase):
    id: int

    class Config:
        orm_mode = True


class MemberUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    age: Optional[int] = None
    allergies: Optional[str] = None
    dislikes: Optional[str] = None
    likes: Optional[str] = None
    favorite_recipes: Optional[str] = None
    dietary_pref: Optional[str] = None


class HouseholdBase(BaseModel):
    name: str


class HouseholdCreate(HouseholdBase):
    budget: Optional[float] = None
    members: List[MemberCreate] = []


class Household(HouseholdBase):
    id: int
    created_at: Optional[datetime]
    budget: Optional[float] = None
    members: List[Member] = []

    class Config:
        orm_mode = True


class ShoppingListItemBase(BaseModel):
    name: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    notes: Optional[str] = None
    shopped: Optional[bool] = None


class ShoppingListItemCreate(BaseModel):
    name: str
    quantity: Optional[float] = 1.0
    unit: Optional[str] = "unit"
    notes: Optional[str] = None
    shopped: Optional[bool] = False


class ShoppingListItem(ShoppingListItemBase):
    id: int

    class Config:
        orm_mode = True


class ShoppingListBase(BaseModel):
    name: Optional[str] = "Weekly"


class ShoppingListCreate(ShoppingListBase):
    household_id: int


class ShoppingList(ShoppingListBase):
    id: int
    created_at: Optional[datetime]
    items: List[ShoppingListItem] = []

    class Config:
        orm_mode = True


class PantryItemBase(BaseModel):
    name: str
    quantity: Optional[float] = 1.0
    unit: Optional[str] = "unit"
    expires_at: Optional[datetime] = None
    staple: Optional[bool] = False


class PantryItemCreate(PantryItemBase):
    pass


class PantryItem(PantryItemBase):
    id: int

    class Config:
        orm_mode = True


class PantryItemUpdate(BaseModel):
    name: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    expires_at: Optional[datetime] = None
    staple: Optional[bool] = None


class HouseholdSettingsBase(BaseModel):
    pricing_enabled: bool = False
    zip_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_miles: float = 5.0


class HouseholdSettingsCreate(HouseholdSettingsBase):
    household_id: int


class HouseholdSettings(HouseholdSettingsBase):
    id: int
    household_id: int

    class Config:
        orm_mode = True


class PricingOffersRequest(BaseModel):
    household_id: int
    query: str
    radius_miles: Optional[float] = None


class Offer(BaseModel):
    provider: str
    store: str
    price: Optional[float] = None
    unit: Optional[str] = None
    url: Optional[str] = None
    promo_text: Optional[str] = None
    distance_miles: Optional[float] = None


class PricingOffersResponse(BaseModel):
    offers: List[Offer]
    normalized_query: Optional[str] = None


class SavedRecipeIngredientBase(BaseModel):
    name: str


class SavedRecipeIngredientCreate(SavedRecipeIngredientBase):
    pass


class SavedRecipeIngredient(SavedRecipeIngredientBase):
    id: int
    recipe_id: int

    class Config:
        orm_mode = True


class SavedRecipeBase(BaseModel):
    title: str
    url: Optional[str] = None
    servings: Optional[int] = None


class SavedRecipeCreate(SavedRecipeBase):
    household_id: int
    ingredients: List[str] = []


class SavedRecipe(SavedRecipeBase):
    id: int
    household_id: int
    created_at: datetime
    ingredients: List[SavedRecipeIngredient] = []

    class Config:
        orm_mode = True
