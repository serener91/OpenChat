"""
Creating Celery instance
"""

from celery import Celery
from dotenv import load_dotenv
import os
from redis.sentinel import Sentinel

load_dotenv()

## Redis + Redis Backend
# celery = Celery(
#     "tasks",
#     broker=str(os.environ.get("CELERY_BROKER")),
#     backend=str(os.environ.get("CELERY_BACKEND"))
# )


## Redis-Sentinel + Redis Backend
# sentinel = Sentinel(sentinels=[('192.168.90.192', 26379), ('192.168.90.192', 26380), ('192.168.90.192', 26381)],
#                     socket_timeout=0.1,
#                     password=None)
# port = sentinel.discover_master('mymaster')[1]
# celery = Celery(
#     "tasks",
#     broker=os.environ.get("CELERY_BROKER"),
#     backend=f"redis://192.168.90.192:{port}/0",
#     broker_transport_options={
#         "master_name": os.environ.get("CELERY_SENTINEL_MASTER", "mymaster"),
#         # Uncomment if Redis requires a password
#         # "sentinel_kwargs": {"password": "your-redis-password"}
#     }
# )


## Redis-Sentinel + SQL backend
# app = Celery(
#     "tasks",
#     broker=os.environ.get("CELERY_BROKER"),
#     backend=os.environ.get("CELERY_BACKEND"),
#     broker_transport_options={
#         "master_name": os.environ.get("CELERY_SENTINEL_MASTER", "mymaster"),
#         # Uncomment if Redis requires a password
#         # "sentinel_kwargs": {"password": "your-redis-password"}
#     }
#
# )


app = Celery("tasks",
             include=[
                 "tasks.file_save",
                 "tasks.db_save",
                 "tasks.redis_cache"
             ]
             )

# Load configuration from celeryconfig.py
app.config_from_object('celeryconfig')

# Auto-discover tasks from the tasks package
# app.autodiscover_tasks(packages=["tasks"])

# Send task-related events so that tasks can be monitored using tools like flower
app.conf.worker_send_task_events = True

print("✅ Celery configuration loaded successfully!")
