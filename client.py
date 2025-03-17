import httpx
import asyncio
from openai import OpenAI


async def concurrent_stream_sse_response(url:str, message: str, client_id: str):
    # Ensures efficient use of async I/O.
    async with httpx.AsyncClient() as client:
        async with client.stream("POST",
                                 url,
                                 json={"message": message, "user_id": client_id},
                                 headers={"Accept": "text/event-stream"}
                                 ) as response:
            # Asynchronously processes streamed data.
            async for line in response.aiter_text():
                if line:
                    print(line, end="", flush=True)
                    # print(f"Client_{client_id}: {line}", end="", flush=True)  # Identify which client received the response


async def concurrent_main(url: str, user_id: str = "beta_tester123"):
    """
    simulate concurrency when making multiple simultaneous requests to the FastAPI streaming endpoint

    messages = ["Hello", "How are you?", "Tell me a joke", "Explain AI briefly", "how do you make good coffee?"]  # Example inputs
    tasks = [concurrent_stream_sse_response(msg, i) for i, msg in enumerate(messages)]  # Create multiple requests
    await asyncio.gather(*tasks)  # Run all tasks concurrently
    """

    messages = ["Explain AI briefly", "how do you make good coffee?", "우리가 나눈 대화를 요약해줘", "심심하다", "겨울철 가습기는 꼭 사용해야할까?"]

    await concurrent_stream_sse_response(url=url,
                                         message=messages[4],
                                         client_id=user_id)


def inference(query=""):
    """
    Call OpenAI-compatiable server
    """
    client = OpenAI(
        api_key="test123",
        base_url="http://192.168.90.192:11280/v1",
    )

    message = [
        {"role": "developer", "content": ""},
        {"role": "user", "content": query}
    ]

    chat_response = client.chat.completions.create(
        model="vllm",
        messages=message,
        temperature=0.75,
        # top_p=0.8,
        # frequency_penalty=1.05,
        # presence_penalty=1.05,
        max_completion_tokens=512,
        stream=True
    )

    response = chat_response.choices[0].message.content
    for chunk in response:
        if chunk:
            text = chunk.choices[0].delta.content
            print(text, end="")


if __name__ == "__main__":
    user = [
        "kitty",
        "bunny",
        "pony"
    ]

    # API_URL = "http://192.168.90.192:8080/models/chatonly"
    API_URL = "http://192.168.90.192:8080/models/v1/chat/completions"

    # Runs the async function in an event loop.
    asyncio.run(concurrent_main(url=API_URL, user_id=user[0]))


