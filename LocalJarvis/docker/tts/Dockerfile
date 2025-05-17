# Dockerfile otimizado para TTS online/offline (gtts + pyttsx3)
FROM python:3.9-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        espeak \
        ffmpeg \
        libasound2 \
        libespeak1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt

COPY tts_server.py /app/tts_server.py
WORKDIR /app
CMD ["uvicorn", "tts_server:app", "--host", "0.0.0.0", "--port", "5002"]
