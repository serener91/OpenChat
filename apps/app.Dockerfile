# Use an official Python runtime as a parent image
FROM python:3.10-slim
LABEL authors="Gukhwan Hyun"
LABEL build_date="2025-03"

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set the working directory in the container
WORKDIR /app

# Copy app source code
COPY app/ .

# Copy Task source code
COPY task_queue/ .

# Copy setups
COPY common/ .

RUN apt update
RUN apt-get install -y default-libmysqlclient-dev build-essential pkg-config
RUN pip install --upgrade pip

#RUN pip install --no-cache-dir -r app_requirements.txt

# Install into a non-virtual environment with uv
RUN uv pip install --system --no-cache-dir -r app_requirements.txt

# Log directory for app
RUN mkdir -p /var/log/gunicorn
RUN mkdir -p /var/run/gunicorn