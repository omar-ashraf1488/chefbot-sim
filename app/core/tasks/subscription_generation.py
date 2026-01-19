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
STATUS_WEIGHTS = [0.70, 0.15, 0.15]  # 70% Active, 15% Paused, 15% Cancelled

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
        
        # Select status with weighted distribution
        status = random.choices(SUBSCRIPTION_STATUSES, weights=STATUS_WEIGHTS)[0]
        
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
