import logging
import os
import json
from dotenv import load_dotenv
import pymysql

from celery_app import app
from utils import RedisBackend, get_redis_connection


# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


@app.task
def save_json_to_file(task_id, user_input, model_response, model_info):
    """Save response as JSON to a file"""

    data = {"user": user_input, "assistant": model_response, "model_info": model_info}

    dir_path = "./conversations"
    file_path = os.path.join(dir_path, f"{task_id}.json")
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            history = json.load(file)

        history[task_id].append(data)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        return f"updated histroy for {task_id}"

    else:
        os.makedirs(dir_path, exist_ok=True)  # Ensure directory exists
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump({task_id: [data]}, f, ensure_ascii=False, indent=2)
        return f"created histroy for {task_id}"


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

    # Cache response
    redis_conn.set(query_cache_key, model_response, 300)

    return "Update and Cached"


@app.task
def save_chat(user_id, user_input, model_response):
    """maybe callback?"""

    connection = None  # Define connection before try

    try:
        connection = pymysql.connect(
            host="192.168.90.192",
            user="admin",
            password="raven",
            database="chat_history",
            charset='utf8mb4',
            port=3308
        )

        with connection.cursor() as cursor:
            insert_query = "INSERT INTO messages (session_id, sender, message_text) VALUES (%s, %s, %s);"
            chat_data = [
                (user_id, "user", user_input),
                (user_id, "assistant", model_response)
            ]

            cursor.executemany(insert_query, chat_data)
            connection.commit()
            # print("Message inserted successfully.")
            return "Message inserted successfully."

    except Exception as e:
        # print(f"error:{e}")
        return f"error:{e}"

    finally:
        if connection:  # Ensure connection exists before closing
            connection.close()

