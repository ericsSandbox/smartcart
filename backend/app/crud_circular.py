"""
CRUD operations for circular items.
Handles loading, storing, and querying items from weekly ad circulars.
"""

import logging
from datetime import datetime, date
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models import CircularItem
from app.schemas import CircularItemCreate, CircularItem as CircularItemSchema

logger = logging.getLogger(__name__)


def create_circular_item(db: Session, item: CircularItemCreate) -> CircularItem:
    """Create a new circular item in database."""
    db_item = CircularItem(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def create_circular_items_bulk(db: Session, items: List[CircularItemCreate]) -> List[CircularItem]:
    """Create multiple circular items at once."""
    db_items = [CircularItem(**item.dict()) for item in items]
    db.add_all(db_items)
    db.commit()
    for item in db_items:
        db.refresh(item)
    return db_items


def clear_circular_items(db: Session, retailer: Optional[str] = None) -> int:
    """Clear old circular items. If retailer specified, only clear that retailer's items."""
    query = db.query(CircularItem)
    
    if retailer:
        query = query.filter(CircularItem.retailer == retailer)
    
    count = query.delete()
    db.commit()
    logger.info(f"Cleared {count} circular items")
    return count


def get_circular_items(
    db: Session,
    retailer: Optional[str] = None,
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[CircularItem]:
    """Get circular items with optional filtering."""
    query = db.query(CircularItem)
    
    if retailer:
        query = query.filter(CircularItem.retailer == retailer)
    
    if category:
        query = query.filter(CircularItem.category == category)
    
    return query.offset(skip).limit(limit).all()


def search_circular_items(
    db: Session,
    search_term: str,
    retailer: Optional[str] = None,
) -> List[CircularItem]:
    """Search for items by name."""
    search_lower = search_term.lower()
    query = db.query(CircularItem).filter(
        CircularItem.item_name.ilike(f"%{search_lower}%")
    )
    
    if retailer:
        query = query.filter(CircularItem.retailer == retailer)
    
    return query.all()


def get_retailers(db: Session) -> List[str]:
    """Get list of all retailers with items in database."""
    results = db.query(CircularItem.retailer).distinct().all()
    return [r[0] for r in results]


def get_categories_for_retailer(db: Session, retailer: str) -> List[str]:
    """Get all categories for a specific retailer."""
    results = (
        db.query(CircularItem.category)
        .filter(CircularItem.retailer == retailer)
        .distinct()
        .all()
    )
    return [r[0] for r in results if r[0]]


def get_item_count(db: Session, retailer: Optional[str] = None) -> int:
    """Get total count of items."""
    query = db.query(CircularItem)
    
    if retailer:
        query = query.filter(CircularItem.retailer == retailer)
    
    return query.count()


def find_price_for_item(
    db: Session,
    item_name: str,
    retailer: Optional[str] = None,
) -> Optional[float]:
    """Find price for a shopping list item in circular."""
    search_lower = item_name.lower()
    query = db.query(CircularItem).filter(
        CircularItem.item_name.ilike(f"%{search_lower}%")
    )
    
    if retailer:
        query = query.filter(CircularItem.retailer == retailer)
    
    result = query.first()
    return result.price if result else None


def get_circular_summary(db: Session) -> dict:
    """Get summary statistics about loaded circulars."""
    total = db.query(CircularItem).count()
    retailers = len(get_retailers(db))
    
    items_by_retailer = {}
    for retailer_name in get_retailers(db):
        count = get_item_count(db, retailer_name)
        items_by_retailer[retailer_name] = count
    
    return {
        "total_items": total,
        "retailers": retailers,
        "items_by_retailer": items_by_retailer,
        "last_updated": datetime.utcnow()
    }
