from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Boolean, Date
from sqlalchemy.orm import relationship
from .database import Base


class CircularItem(Base):
    """Items from weekly ad circulars - loaded on startup from PDFs"""
    __tablename__ = "circular_items"
    id = Column(Integer, primary_key=True, index=True)
    retailer = Column(String, nullable=False, index=True)  # e.g., "Raley's"
    item_name = Column(String, nullable=False, index=True)  # e.g., "Tri Tip Roast"
    price = Column(Float, nullable=False)  # Sale price or regular price
    regular_price = Column(Float, nullable=True)  # Original price before discount (if on sale)
    discount_percent = Column(Float, nullable=True)  # e.g., 50 for "50% OFF"
    unit = Column(String, default="ea")  # e.g., "lb", "ea", "each"
    category = Column(String, nullable=True)  # e.g., "Meat & Seafood"
    source = Column(String, default="pdf")  # "pdf", "website", etc.
    valid_from = Column(Date, nullable=True)
    valid_until = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    

class Household(Base):
    __tablename__ = "households"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    budget = Column(Float, nullable=True)

    members = relationship("Member", back_populates="household", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates="household", cascade="all, delete-orphan")
    pantry_items = relationship("PantryItem", back_populates="household", cascade="all, delete-orphan")
    lists = relationship("ShoppingList", back_populates="household", cascade="all, delete-orphan")


class Member(Base):
    __tablename__ = "members"
    id = Column(Integer, primary_key=True, index=True)
    household_id = Column(Integer, ForeignKey("households.id"))
    name = Column(String, nullable=False)
    role = Column(String, nullable=True, default='adult')
    age = Column(Integer, nullable=True)
    allergies = Column(String, nullable=True)
    dislikes = Column(String, nullable=True)
    likes = Column(String, nullable=True)
    favorite_recipes = Column(String, nullable=True)
    dietary_pref = Column(String, nullable=True)

    household = relationship("Household", back_populates="members")


class Budget(Base):
    __tablename__ = "budgets"
    id = Column(Integer, primary_key=True, index=True)
    household_id = Column(Integer, ForeignKey("households.id"))
    month = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    spent = Column(Float, default=0.0)

    household = relationship("Household", back_populates="budgets")


class PantryItem(Base):
    __tablename__ = "pantry_items"
    id = Column(Integer, primary_key=True, index=True)
    household_id = Column(Integer, ForeignKey("households.id"))
    name = Column(String, nullable=False)
    quantity = Column(Float, default=1.0)
    unit = Column(String, default="unit")
    expires_at = Column(DateTime, nullable=True)
    staple = Column(Boolean, default=False)

    household = relationship("Household", back_populates="pantry_items")


class ShoppingList(Base):
    __tablename__ = "shopping_lists"
    id = Column(Integer, primary_key=True, index=True)
    household_id = Column(Integer, ForeignKey("households.id"))
    name = Column(String, default="Weekly")
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    items = relationship("ShoppingListItem", back_populates="shopping_list", cascade="all, delete-orphan")
    household = relationship("Household", back_populates="lists")


class ShoppingListItem(Base):
    __tablename__ = "shopping_list_items"
    id = Column(Integer, primary_key=True, index=True)
    list_id = Column(Integer, ForeignKey("shopping_lists.id"))
    name = Column(String, nullable=False)
    quantity = Column(Float, default=1.0)
    unit = Column(String, default="unit")
    notes = Column(String, nullable=True)
    shopped = Column(Boolean, default=False)

    shopping_list = relationship("ShoppingList", back_populates="items")


class HouseholdSettings(Base):
    __tablename__ = "household_settings"
    id = Column(Integer, primary_key=True, index=True)
    household_id = Column(Integer, ForeignKey("households.id"), unique=True)
    pricing_enabled = Column(Boolean, default=False)
    zip_code = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    radius_miles = Column(Float, default=5.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    household = relationship("Household")


class SavedRecipe(Base):
    __tablename__ = "saved_recipes"
    id = Column(Integer, primary_key=True, index=True)
    household_id = Column(Integer, ForeignKey("households.id"))
    title = Column(String, nullable=False)
    url = Column(String, nullable=True)
    servings = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    household = relationship("Household")
    ingredients = relationship("SavedRecipeIngredient", back_populates="recipe", cascade="all, delete-orphan")


class SavedRecipeIngredient(Base):
    __tablename__ = "saved_recipe_ingredients"
    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("saved_recipes.id"))
    name = Column(String, nullable=False)

    recipe = relationship("SavedRecipe", back_populates="ingredients")
