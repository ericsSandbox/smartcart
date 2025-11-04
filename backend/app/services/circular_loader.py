"""
Circular loader service - reads PDFs on startup and loads items into database.
"""

import logging
import os
from pathlib import Path
from typing import List, Optional
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session

from app.schemas import CircularItemCreate
from app.crud_circular import create_circular_items_bulk, clear_circular_items, get_item_count
from app.providers.intelligent_extractor import extract_raley_circular

logger = logging.getLogger(__name__)


class CircularLoader:
    """Load and manage circular item data."""
    
    def __init__(self):
        self.circular_dir = os.getenv("CIRCULAR_DIR", "/data/circulars")
        self.auto_load = os.getenv("AUTO_LOAD_CIRCULARS", "true").lower() == "true"
        self.retailers = {
            "Raley's": {
                "pattern": "*raley*.pdf",
                "extractor": self._extract_raleys,
            },
            # Add more retailers as needed
        }
    
    def load_all_circulars(self, db: Session) -> dict:
        """Load all available circulars on startup."""
        results = {
            "loaded": [],
            "failed": [],
            "total_items": 0,
        }
        
        if not self.auto_load:
            logger.info("Auto-load circulars disabled")
            return results
        
        circular_path = Path(self.circular_dir)
        if not circular_path.exists():
            logger.warning(f"Circular directory not found: {self.circular_dir}")
            return results
        
        logger.info(f"Loading circulars from {self.circular_dir}")
        
        for retailer_name, config in self.retailers.items():
            try:
                logger.info(f"Loading {retailer_name} circulars...")
                
                # Find PDF files
                pattern = config["pattern"]
                pdf_files = list(circular_path.glob(pattern))
                
                if not pdf_files:
                    logger.debug(f"No {retailer_name} PDFs found matching {pattern}")
                    continue
                
                # Extract items from PDFs
                extractor = config["extractor"]
                items = extractor(pdf_files)
                
                if items:
                    # Clear old items for this retailer
                    clear_circular_items(db, retailer_name)
                    
                    # Load new items
                    db_items = create_circular_items_bulk(db, items)
                    
                    results["loaded"].append({
                        "retailer": retailer_name,
                        "items": len(db_items),
                        "files": len(pdf_files),
                    })
                    results["total_items"] += len(db_items)
                    
                    logger.info(f"✓ Loaded {len(db_items)} {retailer_name} items from {len(pdf_files)} files")
            
            except Exception as e:
                logger.error(f"Failed to load {retailer_name} circulars: {e}", exc_info=True)
                results["failed"].append({
                    "retailer": retailer_name,
                    "error": str(e),
                })
        
        logger.info(f"Circular loading complete. Total items loaded: {results['total_items']}")
        return results
    
    def _extract_raleys(self, pdf_files: List[Path]) -> List[CircularItemCreate]:
        """Extract items from Raley's PDFs."""
        items = []
        
        # Set valid dates (assume weekly circular, valid for 1 week)
        today = date.today()
        valid_from = today
        valid_until = today + timedelta(days=7)
        
        for pdf_file in pdf_files:
            try:
                logger.debug(f"Extracting from {pdf_file.name}...")
                
                # Use PaddleOCR extraction
                products = extract_raley_circular(str(pdf_file), method='paddle')
                
                for product in products:
                    item = CircularItemCreate(
                        retailer="Raley's",
                        item_name=product.get("name", "Unknown"),
                        price=float(product.get("price", 0)),
                        unit=product.get("unit", "ea"),
                        category=product.get("category", "General"),
                        source="pdf",
                        valid_from=valid_from,
                        valid_until=valid_until,
                    )
                    items.append(item)
                
                logger.debug(f"  Extracted {len(products)} items from {pdf_file.name}")
            
            except Exception as e:
                logger.warning(f"Error extracting from {pdf_file.name}: {e}")
                continue
        
        return items
    
    def reload_retailer(self, db: Session, retailer: str) -> dict:
        """Reload circulars for a specific retailer."""
        if retailer not in self.retailers:
            return {"error": f"Unknown retailer: {retailer}"}
        
        try:
            config = self.retailers[retailer]
            extractor = config["extractor"]
            pattern = config["pattern"]
            
            circular_path = Path(self.circular_dir)
            pdf_files = list(circular_path.glob(pattern))
            
            if not pdf_files:
                return {"error": f"No PDFs found for {retailer}"}
            
            items = extractor(pdf_files)
            
            # Clear and reload
            clear_circular_items(db, retailer)
            db_items = create_circular_items_bulk(db, items)
            
            logger.info(f"Reloaded {len(db_items)} items for {retailer}")
            
            return {
                "retailer": retailer,
                "items_loaded": len(db_items),
                "files": len(pdf_files),
            }
        
        except Exception as e:
            logger.error(f"Failed to reload {retailer}: {e}")
            return {"error": str(e)}


# Global loader instance
_loader: Optional[CircularLoader] = None


def get_loader() -> CircularLoader:
    """Get or create loader instance."""
    global _loader
    if _loader is None:
        _loader = CircularLoader()
    return _loader


def init_circular_loader(db: Session):
    """Initialize circular loader on app startup."""
    loader = get_loader()
    results = loader.load_all_circulars(db)
    
    if results["loaded"]:
        logger.info(f"Loaded {results['total_items']} items from {len(results['loaded'])} retailers")
    
    return results
