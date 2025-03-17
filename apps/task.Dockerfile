# Use an official Python runtime as a parent image
FROM python:3.10-slim
LABEL authors="Gukhwan Hyun"
LABEL build_date="2025-03"

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set the working directory in the container
WORKDIR /app

# Copy Task source code
COPY task_queue/ .

# Copy setups
COPY common/ .

RUN apt update
RUN apt-get install -y default-libmysqlclient-dev build-essential pkg-config
RUN pip install --upgrade pip
#RUN pip install celery openai redis python-dotenv flower fastapi mysql-connector-python SQLAlchemy mysqlclient

# Install into a non-virtual environment with uv
RUN uv pip install --system --no-cache-dir -r task_requirements.txt

RUN groupadd -g 999 celery
RUN useradd -r -u 999 -g celery celery

USER celery