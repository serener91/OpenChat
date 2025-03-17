import time

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from starlette.responses import StreamingResponse
import json
import os
from openai import AsyncOpenAI
# from langfuse.openai import AsyncOpenAI
from dotenv import load_dotenv

from tasks.file_save import save_json_to_file
from tasks.db_save import save_chat
from tasks.redis_cache import postprocess
from utils import RedisBackend, make_query_cache_key, get_redis_connection


load_dotenv()

router = APIRouter(prefix="/models")


class ChatRequest(BaseModel):
    user_id: str
    message: str


class ChatResponse(BaseModel):
    response: str


async def gpt_response(user_input, task_id, cache_key, chat_history, chatonly=False):
    """
    asyncio.run(gpt_response())
    """

    client = AsyncOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY")
    )

    with open(os.environ.get("PROMPT_MANAGER"), "r", encoding="utf-8") as f:
        model_configs = json.load(f)["gpt"]

    if len(chat_history) > 0:
        messages = [
            {"role": "developer", "content": model_configs["system_prompt"]}
        ]
        messages.extend(chat_history)
        messages.extend(
            [{"role": "user", "content": user_input}]
        )

    else:
        messages = [
                {"role": "developer", "content": model_configs["system_prompt"]},
                {"role": "user", "content": user_input}
            ]

    response = await client.chat.completions.create(
        model=str(model_configs["model"]),
        messages=messages,
        temperature=float(model_configs["temperature"]),
        stream=True,
        max_completion_tokens=model_configs["max_token"]
        # metadata={"test": "this is test"}
    )

    response_text = ""
    async for chunk in response:
        if chunk:
            text = chunk.choices[0].delta.content
            if text is not None:
                response_text += text
                yield text

    if not chatonly:
        # save_json_to_file.apply_async(args=[task_id, user_input, response_text, model_configs["model"]])
        postprocess.apply_async(args=[task_id, user_input, response_text, cache_key])
        save_chat.apply_async(args=[task_id, user_input, response_text])


async def vllm_response(user_input, task_id, cache_key, chat_history, chatonly=False):
    """
    asyncio.run(gpt_response())
    """

    client = AsyncOpenAI(
        api_key=os.environ.get("LOCAL_API_KEY", "test123"),
        base_url=os.environ.get("LOCAL_INFERENCE_SERVER", "http://192.168.90.192:11280/v1")
    )

    with open(os.environ.get("PROMPT_MANAGER"), "r", encoding="utf-8") as f:
        model_configs = json.load(f)["vllm"]

    if len(chat_history) > 0:
        messages = [
            {"role": "developer", "content": model_configs["system_prompt"]}
        ]
        messages.extend(chat_history)
        messages.extend(
            [{"role": "user", "content": user_input}]
        )

    else:
        messages = [
            {"role": "developer", "content": model_configs["system_prompt"]},
            {"role": "user", "content": user_input}
        ]

    response = await client.chat.completions.create(
        model=os.environ.get("LOCAL_MODEL", "llm"),
        messages=messages,
        temperature=model_configs["temperature"],
        stream=True,
        frequency_penalty=1.05,
        presence_penalty=1.05,
        max_tokens=model_configs["max_token"]
    )

    response_text = ""
    async for chunk in response:
        text = chunk.choices[0].delta.content
        if text is not None:
            response_text += text
            yield text

    if not chatonly:
        # save_json_to_file.apply_async(args=[task_id, user_input, response_text, model_configs["model"]])
        postprocess.apply_async(args=[task_id, user_input, response_text, cache_key])
        save_chat.apply_async(args=[task_id, user_input, response_text])


@router.post("/chatonly")
async def stream(request: ChatRequest):

    model_response = gpt_response(user_input=request.message, task_id=request.user_id, cache_key=None, chat_history=[], chatonly=True)

    return StreamingResponse(
        model_response,
        media_type="text/event-stream"
    )


@router.post("/v1/chat/completions")
async def main(request: ChatRequest):

    """Main Pipeline"""

    backend = RedisBackend()
    redis_conn = get_redis_connection()

    # 1. Rate limiting check
    backend.check_rate_limit(user_id=request.user_id)

    # 2. Check cache
    query_cache_key = make_query_cache_key(query=request.message)
    query_cache = redis_conn.get(query_cache_key)
    if query_cache:
        # save chat history after respond with cached response
        postprocess.apply_async(args=[request.user_id, request.message, query_cache, query_cache_key])
        save_chat.apply_async(args=[request.user_id, request.message, query_cache])

        return ChatResponse(response=query_cache)

    else:
        history = backend.get_conversation_history(user_id=request.user_id)
        model_response = gpt_response(user_input=request.message, task_id=request.user_id, cache_key=query_cache_key, chat_history=history)
        # model_response = vllm_response(user_input=request.message, task_id=request.user_id, cache_key=query_cache_key, chat_history=chats)

        return StreamingResponse(
            model_response,
            media_type="text/event-stream"
        )





