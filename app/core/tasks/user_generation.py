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


def _create_user(user_repo: UserRepository) -> bool:
    """Create a single user with random data."""
    try:
        gender = random.choice(GENDERS)
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
