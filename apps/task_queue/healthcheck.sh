#!/bin/bash

# Check if Celery workers are alive
# inspect active lists active workers.
# grep -q 'celery@' ensures that at least one worker is active.
# Exits with 0 (healthy) if at least one worker is active, otherwise 1 (unhealthy).
celery -A tasks inspect active 2>/dev/null | grep -q 'celery@' && exit 0 || exit 1
