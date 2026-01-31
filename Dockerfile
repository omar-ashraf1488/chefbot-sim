FROM python:3.14-slim AS builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=2.0.0 \
    POETRY_VIRTUALENVS_CREATE=false \
    PATH="/root/.local/bin:$PATH"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /chefbot-sim

# Copy project files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-root --only main

# Stage 2: Runtime environment
FROM python:3.14-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PATH="/root/.local/bin:$PATH"

# Install only essential runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /chefbot-sim

# Copy app source code
COPY . .

# Copy dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Expose port 8000
EXPOSE 8000

ENTRYPOINT ["/bin/bash", "/chefbot-sim/scripts/entrypoint.sh"]
CMD ["fastapi", "run", "--workers", "1", "app/main.py"]
