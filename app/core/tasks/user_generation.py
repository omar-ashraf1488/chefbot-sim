"""Scheduled task for generating users."""
import logging
import random
from faker import Faker

from app.core.config import settings
from app.core.db import SessionLocal
from app.core.repositories.user_repository import UserRepository
from app.core.scheduler import scheduler

logger = logging.getLogger(__name__)

fake = Faker()

GENDERS = ["Male", "Female"]

# Dynamic settings (can be updated via API)
_user_generation_settings = {
    "male_weight": 0.5,  # Default: 50% Male, 50% Female (calculated automatically)
    "interval": settings.USER_GENERATION_INTERVAL
}


def get_user_generation_settings():
    """Get current user generation settings."""
    settings = _user_generation_settings.copy()
    # Calculate female weight for response
    settings["female_weight"] = 1.0 - settings["male_weight"]
    return settings


def update_user_generation_settings(male_weight=None, interval=None):
    """Update user generation settings.
    
    Args:
        male_weight: Weight for Male gender (0.0 to 1.0). Female weight is automatically 1.0 - male_weight.
        interval: Generation interval in seconds.
    """
    if male_weight is not None:
        if not 0.0 <= male_weight <= 1.0:
            raise ValueError("male_weight must be between 0.0 and 1.0")
        _user_generation_settings["male_weight"] = male_weight
    
    if interval is not None:
        if interval < 1:
            raise ValueError("interval must be at least 1 second")
        _user_generation_settings["interval"] = interval
        _update_scheduler_job()
    
    return get_user_generation_settings()


def _update_scheduler_job():
    """Update the scheduler job interval."""
    job = scheduler.get_job("generate_users")
    if job:
        scheduler.reschedule_job(
            "generate_users",
            trigger="interval",
            seconds=_user_generation_settings["interval"]
        )
        logger.info(f"Updated user generation interval to {_user_generation_settings['interval']} seconds")


def _create_user(user_repo: UserRepository) -> bool:
    """Create a single user with random data."""
    try:
        # Select gender with weighted distribution (using dynamic weights)
        male_weight = _user_generation_settings["male_weight"]
        female_weight = 1.0 - male_weight
        weights = [male_weight, female_weight]
        gender = random.choices(GENDERS, weights=weights)[0]
        first_name = (
            fake.first_name_male() if gender == "Male" 
            else fake.first_name_female()
        )
        
        user_repo.create(
            email=fake.unique.email(),
            first_name=first_name,
            last_name=fake.last_name(),
            timezone=fake.timezone(),
            gender=gender
        )
        return True
    except Exception as e:
        logger.warning(f"Failed to create user: {e}")
        return False


@scheduler.scheduled_job(
    "interval",
    seconds=settings.USER_GENERATION_INTERVAL,
    id="generate_users",
    name="Generate Users",
    max_instances=1
)
def generate_users_task() -> None:
    """Scheduled task to generate N users."""
    if not settings.USER_GENERATION_ENABLED or settings.USER_GENERATION_COUNT <= 0:
        return
    
    logger.info(f"Generating {settings.USER_GENERATION_COUNT} users")
    
    db = SessionLocal()
    try:
        user_repo = UserRepository(db)
        created_count = sum(
            _create_user(user_repo) 
            for _ in range(settings.USER_GENERATION_COUNT)
        )
        logger.info(f"Created {created_count}/{settings.USER_GENERATION_COUNT} users")
    finally:
        db.close()
