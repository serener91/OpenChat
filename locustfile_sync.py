from locust import HttpUser, task, between, events, FastHttpUser
import requests
import time

API_URL = "/stream"


# locust -f locustfile_sync.py --host=http://localhost:8080


class StreamingUser(FastHttpUser):
    wait_time = between(1, 3)

    @task
    def stream_sse(self):
        message = {"message": "Tell me something interesting"}
        self.send_streaming_request(message)

    def send_streaming_request(self, message):
        start_time = time.time()

        with self.client.post(self.host+API_URL, json=message, headers={"Accept": "text/event-stream"},
                              stream=True) as response:
            for line in response.iter_lines():
                if line:
                    pass  # You can log responses if needed

        total_time = int((time.time()-start_time) * 1000)
        events.request.fire(request_type="POST", name="stream_sse_sync", response_time=total_time, response_length=0)
