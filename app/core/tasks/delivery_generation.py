"""Scheduled task for generating deliveries."""
import logging
import random
from datetime import datetime, timedelta
from faker import Faker

from app.core.config import settings
from app.core.db import SessionLocal
from app.core.repositories.delivery_repository import DeliveryRepository
from app.core.repositories.order_repository import OrderRepository
from app.core.scheduler import scheduler

logger = logging.getLogger(__name__)

fake = Faker()

DELIVERY_STATUSES = ["delivered", "delayed", "failed", "in_transit"]
STATUS_WEIGHTS = [0.60, 0.15, 0.05, 0.20]  # 60% delivered, 15% delayed, 5% failed, 20% in_transit


def _create_delivery(
    delivery_repo: DeliveryRepository,
    order
) -> bool:
    """Create a single delivery with random data."""
    try:
        # Check if delivery already exists (unique constraint)
        existing = delivery_repo.get_by_order_id(order.id)
        if existing:
            return False  # Skip if delivery already exists
        
        # Select status with weighted distribution
        status = random.choices(DELIVERY_STATUSES, weights=STATUS_WEIGHTS)[0]
        
        # Expected delivery: 2-5 days after order date
        days_after_order = random.randint(2, 5)
        expected_delivery_date = order.order_date + timedelta(days=days_after_order)
        
        # Actual delivery date based on status
        actual_delivery_date = None
        if status == "delivered":
            # Delivered: on time or ±1 day
            days_offset = random.randint(-1, 1)
            actual_delivery_date = expected_delivery_date + timedelta(days=days_offset)
        elif status == "delayed":
            # Delayed: 1-3 days after expected
            days_offset = random.randint(1, 3)
            actual_delivery_date = expected_delivery_date + timedelta(days=days_offset)
        # For "failed" or "in_transit", actual_delivery_date stays None
        
        # Tracking number (70% chance)
        tracking_number = None
        if random.random() < 0.7:
            tracking_number = f"TRACK{random.randint(100000, 999999)}"
        
        # Notes (30% chance)
        notes = None
        if random.random() < 0.3:
            note_options = [
                "Left at front door",
                "Left with neighbor",
                "Delivered to mailbox",
                "Customer complaint",
                "Package damaged"
            ]
            notes = random.choice(note_options)
        
        delivery_repo.create(
            order_id=order.id,
            status=status,
            expected_delivery_date=expected_delivery_date,
            actual_delivery_date=actual_delivery_date,
            tracking_number=tracking_number,
            notes=notes
        )
        return True
    except Exception as e:
        logger.warning(f"Failed to create delivery: {e}")
        return False


@scheduler.scheduled_job(
    "interval",
    seconds=settings.DELIVERY_GENERATION_INTERVAL,
    id="generate_deliveries",
    name="Generate Deliveries",
    max_instances=1
)
def generate_deliveries_task() -> None:
    """Scheduled task to generate N deliveries."""
    
    logger.info(f"Generating {settings.DELIVERY_GENERATION_COUNT} deliveries")
    
    db = SessionLocal()
    try:
        delivery_repo = DeliveryRepository(db)
        order_repo = OrderRepository(db)
        
        # Get orders (preferably shipped or delivered status)
        orders = order_repo.get_all(limit=1000)
        if not orders:
            logger.warning("No orders found. Skipping delivery generation.")
            return
        
        # Filter orders that don't have deliveries yet
        orders_without_delivery = []
        for order in orders:
            existing = delivery_repo.get_by_order_id(order.id)
            if not existing:
                orders_without_delivery.append(order)
        
        if not orders_without_delivery:
            logger.warning("All orders already have deliveries. Skipping delivery generation.")
            return
        
        # Limit to requested count
        selected_orders = random.sample(
            orders_without_delivery,
            min(settings.DELIVERY_GENERATION_COUNT, len(orders_without_delivery))
        )
        
        created_count = sum(
            _create_delivery(delivery_repo, order)
            for order in selected_orders
        )
        logger.info(f"Created {created_count}/{len(selected_orders)} deliveries")
    finally:
        db.close()
