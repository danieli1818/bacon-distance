FROM python:3.10-slim
LABEL authors="Daniel Rottner"

# Build-time argument: environment (default to "production")
ARG ENV=production
ENV ENV=${ENV}

# Setting the workdir
WORKDIR /app

# Copy and install system dependencies
COPY system-requirements.txt ./
COPY system-requirements-dev.txt ./

RUN apt-get update && \
    xargs -a system-requirements.txt apt-get install -y --no-install-recommends && \
    if [ "$ENV" = "development" ]; then \
        xargs -a system-requirements-dev.txt apt-get install -y --no-install-recommends; \
    fi && \
    rm -rf /var/lib/apt/lists/*  # Cleans up the local apt package cache to save space

# Copy Python requirements
COPY requirements.txt .
COPY requirements-dev.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    if [ "$ENV" = "development" ]; then \
        pip install --no-cache-dir -r requirements-dev.txt; \
    fi

# Copy relevant code
COPY bacondistance bacondistance/
COPY frontend frontend/

# Install requirements
RUN pip install --no-cache-dir -r requirements.txt
