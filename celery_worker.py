import os
from celery import Celery

REDIS_URL = os.getenv("REDIS_URL")

celery = Celery(
    "worker",
    broker=REDIS_URL,
    backend=REDIS_URL
)