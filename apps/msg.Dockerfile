FROM redis:latest
LABEL authors="Gukhwan Hyun"
LABEL build_date="2025-03"

WORKDIR /app

# Copy Redis configs
COPY message_queue/ .

