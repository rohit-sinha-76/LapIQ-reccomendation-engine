FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy package metadata and source code
COPY pyproject.toml README.md /app/
COPY src /app/src
COPY tests /app/tests

# Install python package and dependencies
RUN pip install --no-cache-dir -e .[dev]

EXPOSE 8000

CMD ["uvicorn", "lapiq.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
