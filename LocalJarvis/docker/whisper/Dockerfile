# Dockerfile otimizado para CPU/WSL, sem dependências de CUDA/nvidia
FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y ffmpeg python3-pip && \
    rm -rf /var/lib/apt/lists/* && \
    pip3 install --upgrade pip && \
    pip3 install --no-cache-dir fastapi uvicorn openai-whisper torch==2.0.1

COPY whisper_server.py /app/whisper_server.py
WORKDIR /app
CMD ["uvicorn", "whisper_server:app", "--host", "0.0.0.0", "--port", "5001"]
