"""Scheduled task for generating recipes."""
import logging
import random
from decimal import Decimal
from faker import Faker

from app.core.config import settings
from app.core.db import SessionLocal
from app.core.repositories.recipe_repository import RecipeRepository
from app.core.scheduler import scheduler

logger = logging.getLogger(__name__)

fake = Faker()

# Predefined recipe tags for realistic categorization
RECIPE_TAGS = [
    "Keto",
    "Vegetarian",
    "Vegan",
    "Gluten-Free",
    "Dairy-Free",
    "Family-Friendly",
    "Quick",
    "Comfort Food",
    "Healthy",
    "Low-Carb",
    "High-Protein",
    "Mediterranean",
    "Asian",
    "Italian",
    "Mexican",
    "Spicy",
    "Kid-Friendly",
    "Date Night",
    "Meal Prep",
    "Pescatarian"
]

# Recipe name templates for more realistic meal kit recipe names
RECIPE_NAME_TEMPLATES = [
    "{protein} {cuisine} Bowl",
    "{protein} {cooking_method} with {side}",
    "{cuisine} {protein} {dish_type}",
    "{flavor} {protein} {base}",
    "{protein} {style} {cuisine}",
    "Grilled {protein} {side}",
    "Pan-Seared {protein} {accompaniment}",
    "{cuisine} {protein} Skillet",
]

PROTEINS = ["Chicken", "Salmon", "Beef", "Turkey", "Pork", "Tofu", "Shrimp", "Cod"]
CUISINES = ["Thai", "Italian", "Mexican", "Mediterranean", "Asian", "Indian", "French", "American"]
COOKING_METHODS = ["Teriyaki", "Herb-Crusted", "Balsamic", "Lemon", "Garlic", "Spicy"]
SIDES = ["Rice", "Quinoa", "Pasta", "Potatoes", "Vegetables", "Salad", "Couscous"]
DISH_TYPES = ["Stir-Fry", "Skillet", "Casserole", "Wrap", "Pasta", "Bowl", "Tacos"]
FLAVORS = ["Honey", "Sesame", "Cilantro", "Rosemary", "Basil", "Ginger"]
BASES = ["Pasta", "Rice Bowl", "Quinoa Bowl", "Noodles", "Salad"]
STYLES = ["Classic", "Herbed", "Spiced", "Marinated", "Glazed"]
ACCOMPANIMENTS = ["Asparagus", "Broccoli", "Green Beans", "Sweet Potatoes", "Brussels Sprouts"]


def _generate_recipe_name() -> str:
    """Generate a realistic recipe name using templates."""
    template = random.choice(RECIPE_NAME_TEMPLATES)
    
    return template.format(
        protein=random.choice(PROTEINS),
        cuisine=random.choice(CUISINES),
        cooking_method=random.choice(COOKING_METHODS),
        side=random.choice(SIDES),
        dish_type=random.choice(DISH_TYPES),
        flavor=random.choice(FLAVORS),
        base=random.choice(BASES),
        style=random.choice(STYLES),
        accompaniment=random.choice(ACCOMPANIMENTS)
    )


def _generate_tags() -> list[str]:
    """Generate random tags for a recipe (1-4 tags)."""
    num_tags = random.randint(1, 4)
    return random.sample(RECIPE_TAGS, num_tags)


def _create_recipe(recipe_repo: RecipeRepository) -> bool:
    """Create a single recipe with random data."""
    try:
        # Generate name
        name = _generate_recipe_name()
        
        # Generate optional description (70% chance)
        description = None
        if random.random() < 0.7:
            description = fake.text(max_nb_chars=200)
        
        # Generate calories (300-800 range)
        calories = random.randint(300, 800)
        
        # Generate tags
        tags = _generate_tags()
        
        # Generate price (15.99 - 34.99)
        price = Decimal(str(round(random.uniform(15.99, 34.99), 2)))
        
        # Generate preparation time (20-60 minutes)
        preparation_time = random.randint(20, 60)
        
        # Generate servings (2-6)
        servings = random.randint(2, 6)
        
        # Generate optional image URL (60% chance)
        image_url = None
        if random.random() < 0.6:
            image_url = fake.image_url()
        
        recipe_repo.create(
            name=name,
            description=description,
            calories=calories,
            tags=tags,
            price=price,
            preparation_time=preparation_time,
            servings=servings,
            image_url=image_url
        )
        return True
    except Exception as e:
        logger.warning(f"Failed to create recipe: {e}")
        return False


@scheduler.scheduled_job(
    "interval",
    seconds=settings.RECIPE_GENERATION_INTERVAL,
    id="generate_recipes",
    name="Generate Recipes",
    max_instances=1
)
def generate_recipes_task() -> None:
    """Scheduled task to generate N recipes."""
    if not settings.RECIPE_GENERATION_ENABLED or settings.RECIPE_GENERATION_COUNT <= 0:
        return
    
    logger.info(f"Generating {settings.RECIPE_GENERATION_COUNT} recipes")
    
    db = SessionLocal()
    try:
        recipe_repo = RecipeRepository(db)
        created_count = sum(
            _create_recipe(recipe_repo)
            for _ in range(settings.RECIPE_GENERATION_COUNT)
        )
        logger.info(f"Created {created_count}/{settings.RECIPE_GENERATION_COUNT} recipes")
    finally:
        db.close()
