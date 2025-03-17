import pymysql
import os
from celery_app import app


@app.task
def save_chat(user_id, user_input, model_response):
    """maybe callback?"""

    connection = None  # Define connection before try

    try:
        connection = pymysql.connect(
            host=str(os.environ.get("DB_IP", None)),
            user=str(os.environ.get("MARIADB_USER", None)),
            password=str(os.environ.get("MARIADB_PASSWORD", None)),
            database=str(os.environ.get("MARIADB_DATABASE", None)),
            charset='utf8mb4',
            port=int(os.environ.get("MARIADB_PORT", None))
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
