FROM python:3.11-slim as python-base

# Poetry configuration
ENV POETRY_VERSION=1.7.1
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VENV=/opt/poetry-venv
ENV POETRY_CACHE_DIR=/opt/.cache

# Install poetry separated from system interpreter
FROM python-base as poetry-base
RUN python3 -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
    && $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}

# Build final image
FROM python-base as final

# Copy Poetry to final image
COPY --from=poetry-base ${POETRY_VENV} ${POETRY_VENV}

# Add Poetry to PATH
ENV PATH="${PATH}:${POETRY_VENV}/bin"

WORKDIR /app

# Copy project files
COPY backend ./backend
COPY backend/pyproject.toml ./

WORKDIR /app/backend

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-cache

# Set environment variables
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Debug: List contents to verify file structure
RUN ls -la /app && ls -la /app/backend

# Run the application
CMD ["poetry", "run", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]