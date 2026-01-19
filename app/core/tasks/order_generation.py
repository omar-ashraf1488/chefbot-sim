"""Scheduled task for generating orders."""
import logging
import random
from datetime import datetime, timedelta
from decimal import Decimal
from faker import Faker

from app.core.config import settings
from app.core.db import SessionLocal
from app.core.repositories.order_repository import OrderRepository
from app.core.repositories.subscription_repository import SubscriptionRepository
from app.core.repositories.recipe_repository import RecipeRepository
from app.core.scheduler import scheduler

logger = logging.getLogger(__name__)

fake = Faker()

ORDER_STATUSES = ["pending", "shipped", "delivered", "cancelled"]

# Dynamic settings (can be updated via API)
_order_generation_settings = {
    "status_weights": [0.15, 0.20, 0.60, 0.05],  # Default: 15% pending, 20% shipped, 60% delivered, 5% cancelled
    "interval": settings.ORDER_GENERATION_INTERVAL
}


def get_order_generation_settings():
    """Get current order generation settings."""
    return _order_generation_settings.copy()


def update_order_generation_settings(status_weights=None, interval=None):
    """Update order generation settings."""
    if status_weights is not None:
        if len(status_weights) != 4:
            raise ValueError("status_weights must have exactly 4 values")
        if abs(sum(status_weights) - 1.0) > 0.01:
            raise ValueError("status_weights must sum to approximately 1.0")
        _order_generation_settings["status_weights"] = status_weights
    
    if interval is not None:
        if interval < 1:
            raise ValueError("interval must be at least 1 second")
        _order_generation_settings["interval"] = interval
        _update_scheduler_job()
    
    return _order_generation_settings.copy()


def _update_scheduler_job():
    """Update the scheduler job interval."""
    job = scheduler.get_job("generate_orders")
    if job:
        scheduler.reschedule_job(
            "generate_orders",
            trigger="interval",
            seconds=_order_generation_settings["interval"]
        )
        logger.info(f"Updated order generation interval to {_order_generation_settings['interval']} seconds")


def _select_weighted_status() -> str:
    """Select order status with weighted probability."""
    weights = _order_generation_settings["status_weights"]
    return random.choices(ORDER_STATUSES, weights=weights)[0]


def _calculate_total_amount(recipes: list[dict], recipe_prices: dict) -> Decimal:
    """Calculate total amount from recipe prices."""
    total = Decimal("0.00")
    for recipe in recipes:
        recipe_id_str = str(recipe["id"])
        price = recipe_prices.get(recipe_id_str)
        if price:
            total += Decimal(str(price))
    
    # If no prices available, use random amount
    if total == Decimal("0.00"):
        total = Decimal(str(round(random.uniform(20.00, 100.00), 2)))
    
    return total


def _create_order(
    order_repo: OrderRepository,
    subscription_repo: SubscriptionRepository,
    recipe_repo: RecipeRepository,
    active_subscriptions: list,
    available_recipes: list
) -> bool:
    """Create a single order with random data."""
    try:
        # Select random active subscription
        subscription = random.choice(active_subscriptions)
        
        # Select 1-4 random recipes
        num_recipes = random.randint(1, min(4, len(available_recipes)))
        selected_recipes = random.sample(available_recipes, num_recipes)
        
        # Build recipes JSON array
        recipes_json = [
            {"id": str(recipe.id), "name": recipe.name}
            for recipe in selected_recipes
        ]
        
        # Build price lookup for calculation
        recipe_prices = {str(recipe.id): recipe.price for recipe in selected_recipes if recipe.price}
        
        # Calculate total amount
        total_amount = _calculate_total_amount(recipes_json, recipe_prices)
        
        # Select status with weighted distribution
        status = _select_weighted_status()
        
        # Random order date within last 3 months
        days_ago = random.randint(0, 90)
        order_date = datetime.utcnow() - timedelta(days=days_ago)
        
        order_repo.create(
            subscription_id=subscription.id,
            recipes=recipes_json,
            total_amount=total_amount,
            status=status,
            order_date=order_date
        )
        return True
    except Exception as e:
        logger.warning(f"Failed to create order: {e}")
        return False


@scheduler.scheduled_job(
    "interval",
    seconds=settings.ORDER_GENERATION_INTERVAL,
    id="generate_orders",
    name="Generate Orders",
    max_instances=1
)
def generate_orders_task() -> None:
    """Scheduled task to generate N orders."""
    if not settings.ORDER_GENERATION_ENABLED or settings.ORDER_GENERATION_COUNT <= 0:
        return
    
    logger.info(f"Generating {settings.ORDER_GENERATION_COUNT} orders")
    
    db = SessionLocal()
    try:
        order_repo = OrderRepository(db)
        subscription_repo = SubscriptionRepository(db)
        recipe_repo = RecipeRepository(db)
        
        # Get active subscriptions
        active_subscriptions = subscription_repo.get_all(status="Active", limit=1000)
        if not active_subscriptions:
            logger.warning("No active subscriptions found. Skipping order generation.")
            return
        
        # Get available recipes
        available_recipes = recipe_repo.get_all(limit=1000)
        if not available_recipes:
            logger.warning("No recipes found. Skipping order generation.")
            return
        
        created_count = sum(
            _create_order(
                order_repo,
                subscription_repo,
                recipe_repo,
                active_subscriptions,
                available_recipes
            )
            for _ in range(settings.ORDER_GENERATION_COUNT)
        )
        logger.info(f"Created {created_count}/{settings.ORDER_GENERATION_COUNT} orders")
    finally:
        db.close()
