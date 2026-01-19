"""Scheduled task for generating subscriptions."""
import logging
import random
from datetime import datetime, timedelta
from faker import Faker

from app.core.config import settings
from app.core.db import SessionLocal
from app.core.repositories.subscription_repository import SubscriptionRepository
from app.core.repositories.user_repository import UserRepository
from app.core.scheduler import scheduler

logger = logging.getLogger(__name__)

fake = Faker()

SUBSCRIPTION_STATUSES = ["Active", "Paused", "Cancelled"]

# Dynamic settings (can be updated via API)
_subscription_generation_settings = {
    "status_weights": [0.70, 0.15, 0.15],  # Default: 70% Active, 15% Paused, 15% Cancelled
    "interval": settings.SUBSCRIPTION_GENERATION_INTERVAL
}


def get_subscription_generation_settings():
    """Get current subscription generation settings."""
    return _subscription_generation_settings.copy()


def update_subscription_generation_settings(status_weights=None, interval=None):
    """Update subscription generation settings."""
    if status_weights is not None:
        if len(status_weights) != 3:
            raise ValueError("status_weights must have exactly 3 values")
        if abs(sum(status_weights) - 1.0) > 0.01:
            raise ValueError("status_weights must sum to approximately 1.0")
        _subscription_generation_settings["status_weights"] = status_weights
    
    if interval is not None:
        if interval < 1:
            raise ValueError("interval must be at least 1 second")
        _subscription_generation_settings["interval"] = interval
        # Update scheduler job
        _update_scheduler_job()
    
    return _subscription_generation_settings.copy()


def _update_scheduler_job():
    """Update the scheduler job interval."""
    job = scheduler.get_job("generate_subscriptions")
    if job:
        scheduler.reschedule_job(
            "generate_subscriptions",
            trigger="interval",
            seconds=_subscription_generation_settings["interval"]
        )
        logger.info(f"Updated subscription generation interval to {_subscription_generation_settings['interval']} seconds")

# Simple preference options
PREFERENCE_OPTIONS = [
    {"dietary_restrictions": ["No Fish"]},
    {"dietary_restrictions": ["Vegan"]},
    {"dietary_restrictions": ["Vegetarian"]},
    {"allergies": ["Nuts"]},
    {"allergies": ["Dairy"]},
    {"preferences": ["Spicy"]},
    None,  # No preferences
]


def _create_subscription(
    subscription_repo: SubscriptionRepository,
    available_users: list
) -> bool:
    """Create a single subscription with random data."""
    try:
        # Select random user
        user = random.choice(available_users)
        
        # Select status with weighted distribution (using dynamic weights)
        weights = _subscription_generation_settings["status_weights"]
        status = random.choices(SUBSCRIPTION_STATUSES, weights=weights)[0]
        
        # Random preferences (50% chance)
        preferences = None
        if random.random() < 0.5:
            preferences = random.choice([p for p in PREFERENCE_OPTIONS if p is not None])
        
        # Random started_at within last year
        days_ago = random.randint(0, 365)
        started_at = datetime.utcnow() - timedelta(days=days_ago)
        
        subscription_repo.create(
            user_id=user.id,
            status=status,
            preferences=preferences,
            started_at=started_at
        )
        return True
    except Exception as e:
        logger.warning(f"Failed to create subscription: {e}")
        return False


@scheduler.scheduled_job(
    "interval",
    seconds=settings.SUBSCRIPTION_GENERATION_INTERVAL,
    id="generate_subscriptions",
    name="Generate Subscriptions",
    max_instances=1
)
def generate_subscriptions_task() -> None:
    """Scheduled task to generate N subscriptions."""
    
    logger.info(f"Generating {settings.SUBSCRIPTION_GENERATION_COUNT} subscriptions")
    
    db = SessionLocal()
    try:
        subscription_repo = SubscriptionRepository(db)
        user_repo = UserRepository(db)
        
        # Get available users
        available_users = user_repo.get_all(limit=1000)
        if not available_users:
            logger.warning("No users found. Skipping subscription generation.")
            return
        
        created_count = sum(
            _create_subscription(subscription_repo, available_users)
            for _ in range(settings.SUBSCRIPTION_GENERATION_COUNT)
        )
        logger.info(f"Created {created_count}/{settings.SUBSCRIPTION_GENERATION_COUNT} subscriptions")
    finally:
        db.close()
