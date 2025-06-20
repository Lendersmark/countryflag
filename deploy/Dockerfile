FROM python:3.9-slim

LABEL maintainer="Countryflag Team <admin@countryflag.example.com>"
LABEL description="Countryflag API service container"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install required packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy package source code
COPY src/ /app/src/
COPY setup.py README.md /app/

# Install the package
RUN pip install -e .

# Expose port for the API service
EXPOSE 8000

# Set up a non-root user
RUN useradd -m countryuser
USER countryuser

# Command to run the application
CMD ["uvicorn", "countryflag.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
