"""APScheduler service for managing scheduled tasks."""
import logging
from zoneinfo import ZoneInfo
from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import settings

logger = logging.getLogger(__name__)

# Get timezone from settings or default to UTC
timezone = ZoneInfo(settings.SCHEDULER_TIMEZONE)
scheduler = BackgroundScheduler(timezone=timezone)


def start_scheduler() -> None:
    """Start the scheduler and register all scheduled tasks."""
    if not settings.SCHEDULER_ENABLED:
        logger.info("Scheduler is disabled in configuration")
        return
    
    if scheduler.running:
        logger.warning("Scheduler is already running")
        return
    
    logger.info("Starting APScheduler...")
    
    # Register scheduled tasks
    _register_tasks()
    
    # Start scheduler
    scheduler.start()
    logger.info("APScheduler started successfully")


def stop_scheduler() -> None:
    """Stop the scheduler gracefully."""
    if not scheduler.running:
        logger.warning("Scheduler is not running")
        return
    
    logger.info("Stopping APScheduler...")
    scheduler.shutdown(wait=True)
    logger.info("APScheduler stopped")


def _register_tasks() -> None:
    """Import tasks to register them with the scheduler."""
    # Import tasks module to trigger decorator registration
    from app.core.tasks import user_generation  # noqa: F401
    from app.core.tasks import recipe_generation  # noqa: F401
    #from app.core.tasks import order_generation  # noqa: F401


def get_scheduler() -> BackgroundScheduler:
    """Get the scheduler instance."""
    return scheduler
