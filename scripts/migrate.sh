#!/bin/bash

# Migration automation script
# Usage: ./scripts/migrate.sh "Add Product model"

# Check if message argument is provided
if [ -z "$1" ]; then
    echo "Error: Migration message is required"
    echo "Usage: ./scripts/migrate.sh \"Your migration message\""
    exit 1
fi

MIGRATION_MSG="$1"

echo "Creating migration with message: $MIGRATION_MSG"
poetry run alembic revision --autogenerate -m "$MIGRATION_MSG"

if [ $? -eq 0 ]; then
    echo "Migration created successfully!"
    echo "Applying migration to database..."
    poetry run alembic upgrade head
    if [ $? -eq 0 ]; then
        echo "Migration applied successfully!"
    else
        echo "Error: Failed to apply migration"
        exit 1
    fi
else
    echo "Error: Failed to create migration"
    exit 1
fi

