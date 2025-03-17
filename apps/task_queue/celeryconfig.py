"""
Celery configuration
"""
import os

# Broker
broker_url = os.environ.get("CELERY_BROKER")

# Using the database as backend to store task state and results.
result_backend = os.environ.get("CELERY_BACKEND")

# Redis Sentinel settings
broker_transport_options = {
    "master_name": os.environ.get("CELERY_SENTINEL_MASTER", "mymaster"),
    # Uncomment if Redis requires a password
    # "sentinel_kwargs": {"password": os.environ.get("REDIS_PASSWORD")}
}

timezone = "Asia/Seoul"
# task_send_sent_event = False
task_annotations = {'*': {'rate_limit': '10/s'}}

# Task serialization settings
# task_serializer = "json"
# result_serializer = "json"
# accept_content = ["json"]


# Flower settings
flower_port = os.environ.get("FLOWER_PORT", "5555")

# Timeout for All Tasks (Global)
# Soft time limit: Raises an exception if exceeded. (seconds)
CELERY_TASK_SOFT_TIME_LIMIT = 300

# Hard time limit: Kills the task forcefully. (seconds)
CELERY_TASK_TIME_LIMIT = 600
