from fastapi import HTTPException
from datetime import datetime
import hashlib
import json
import redis
import sys
from dotenv import load_dotenv
import os
import secrets
from redis.sentinel import Sentinel
import time


load_dotenv()


def generate_secret_token():
    # Generates a secure URL-safe string
    api_key = secrets.token_urlsafe(32)

    # Generates a secure hex string
    # api_key = secrets.token_hex(32)

    return f"sk-{api_key}"


def get_msg_byte_size(msg: str):
    """
    KB = Byte / 1024 (1024)
    MB = Byte / 1024 / 1024 (1024**2)
    GB = Byte / 1024 / 1024 / 1024 (1024**3)
    """

    return sys.getsizeof(msg)


def get_redis_connection():
    wait_cnt = 2
    try:
        redis_conn = connect_redis()
        if redis_conn is None and wait_cnt != 0:
            time.sleep(1)
            get_redis_connection()
            wait_cnt -= 1
            return redis_conn
        elif redis_conn is None and wait_cnt == 0:
            raise HTTPException(status_code=500, detail="Cannot connect to Redis")

        else:
            return redis_conn

    except Exception as e:
        print(f"Error: {e}")
        return None
    except redis.exceptions.ConnectionError as e:
        return f"Connection refused: {e}"


def connect_redis(use_sentinel=True):

    """
    Returns a Redis connection dynamically by discovering the current master.
    """

    if use_sentinel:
        system_ipaddr = str(os.environ.get("REDIS_IP", None))
        sentinel = Sentinel(sentinels=[
            (system_ipaddr, int(os.environ.get("SENTINEL_PORT1", 26379))),
            (system_ipaddr, int(os.environ.get("SENTINEL_PORT2", 26380))),
            (system_ipaddr, int(os.environ.get("SENTINEL_PORT3", 26381)))
        ],
                            socket_timeout=0.1,
                            password=None)
        try:
            master = sentinel.discover_master('mymaster')
            return redis.Redis(host=master[0], port=master[1], db=0, decode_responses=True, password=None)
        except Exception as e:
            print(f"Error connecting to Redis Sentinel: {e}")
            return None

    redis_conn = redis.Redis(
        host=str(os.environ.get("REDIS_IP", None)),
        port=int(os.environ.get("REDIS_PORT", 6379)),
        db=int(os.environ.get("REDIS_DB", 0)),
        password=None,
        decode_responses=True
    )

    return redis_conn


def make_rate_limit_key(user_id: str) -> str:
    """Make an identifier based on provided user id to track the number of request"""

    return f"limiter:{user_id}"


def make_query_cache_key(query: str) -> str:
    """

    Cache the user query.
    Use hash for safekeeping

    :param query: 사용자 샘플 질문!
    :return: cache:d1826af4ee1c519c46707c27e753558794eb362f1e1c74a90344acd8339b4a0c
    """

    return f"cache:{hashlib.sha256(query.strip().lower().encode()).hexdigest()}"


def make_chat_key(user_id: str) -> str:
    """
    Make an identifier to save conversation between user and system
    """

    return f"chat:{user_id}"


class RedisBackend:

    def __init__(self):
        self.redis_conn = connect_redis(use_sentinel=True)

    def get_conversation_history(self, user_id: str, max_messages: int = 20) -> list:

        key = make_chat_key(user_id)

        # Get last N (max_messages) messages
        history = []
        msgs = self.redis_conn.lrange(key, -max_messages, -1)
        for msg in msgs:
            text = json.loads(msg)
            text.pop('timestamp')
            history.append(text)

        return history

    def store_message(self, user_id: str, role: str, content: str):

        key = make_chat_key(user_id)

        # Format the message as JSON-string
        message = json.dumps(
            {
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat(sep='_')
            },
            ensure_ascii=False
        )

        # Save a message to Redis as Queue
        self.redis_conn.rpush(key, message)

        # Trim conversation history to last 20 messages
        self.redis_conn.ltrim(key, -20, -1)

    def check_rate_limit(self, user_id: str):

        """
        Rate limiting middleware
        """

        key = make_rate_limit_key(user_id)

        # 10 requests / minute
        threshold_val = 10
        unit_time = 60

        # Atomically increment the counter for the current window
        current_state = self.redis_conn.incr(key)

        if current_state == 1:
            self.redis_conn.expire(key, unit_time)

        if current_state > threshold_val:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded"
            )


if __name__ == '__main__':
    # a = RedisBackend().get_conversation_history(user_id="alpha")
    # for i in a:
    #     i = json.loads(i)
    #     i.pop("timestamp")
    #     print(i)

    a = RedisBackend().redis_conn
    # a.set("message", "Hello, Redis!")
    # # b = a.get("message")
    # # print(b)
    #
    # data1 = {"role": "user", "content": "how do you make good coffee?"}
    # data2 = {"role": "assistant", "content": "좋은 커피를 만드는 방법은 여러 가지가 있지만, 기본적인 단계는 다음과 같습니다:\n\n1. **좋은 원두 선택**: 신선하고 품질 좋은 원두를 선택하세요. 원두의 종류와 로스팅 정도에 따라 맛이 달라집니다.\n\n2. **정확한 분쇄**: 원두를 커피의 추출 방법에 맞게 적절한 크기로 분쇄합니다. 예를 들어, 에스프레소는 미세하게, 프렌치 프레스는 굵게 분쇄해야 합니다.\n\n3. **물의 온도**: 커피를 추출할 때 물의 온도는 약 90-96도 사이가 이상적입니다. 너무 뜨거운 물은 쓴맛을 낼 수 있습니다.\n\n4. **커피와 물의 비율**: 일반적으로 커피와 물의 비율은 1:15에서 1:18 정도가 좋습니다. 취향에 따라 조절할 수 있습니다.\n\n5. **적절한 추출 시간**: 추출 시간도 중요합니다. 예를 들어, 에스프레소는 약 25-30초, 드립 커피는 4-5분 정도가 적당합니다.\n\n6. **신선한 물 사용**: 깨끗하고 신선한 물을 사용하는 것이 중요합니다. 물의 맛이 커피에 영향을 줄 수 있습니다.\n\n이 과정을 통해 자신만의 완벽한 커피를 만들어보세요!"}
    #
    # # a.rpush("messages", "Hello", "World", "Redis!")
    # a.rpush("omega", json.dumps(data1, ensure_ascii=False), json.dumps(data2, ensure_ascii=False))
    # a.hset("user:1", mapping={"name": "Francis", "message": "Hello, Francis!"})
    #
    # res1 = a.xadd(
    #     "race:france",
    #     {"rider": "Castilla", "speed": 30.2, "position": 1, "location_id": 1},
    # )
    # print(res1)
    print(a.xlen("race:france"))
    res5 = a.xread(streams={"race:france": 0}, count=100, block=300)
    print(
        res5
    )
