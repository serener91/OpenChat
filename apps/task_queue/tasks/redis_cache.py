from celery_app import app
from utils import RedisBackend, get_redis_connection


@app.task
def postprocess(task_id, user_input, model_response, query_cache_key):
    """
    Update conversation history
    Cache response

    """
    redis_conn = get_redis_connection()
    backend = RedisBackend()

    # Update conversation history
    backend.store_message(user_id=task_id, role="user", content=user_input)
    backend.store_message(user_id=task_id, role="assistant", content=model_response)

    # Cache response (600 seconds)
    redis_conn.set(query_cache_key, model_response, ex=600)

    return "Update and Cached"
