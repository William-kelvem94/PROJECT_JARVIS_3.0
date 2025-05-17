# Dockerfile otimizado para suporte a GPU (CUDA) e whisper
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y ffmpeg python3-pip && \
    rm -rf /var/lib/apt/lists/* && \
    pip3 install --upgrade pip && \
    pip3 install --no-cache-dir fastapi uvicorn openai-whisper torch==2.1.0+cu118 --extra-index-url https://download.pytorch.org/whl/cu118

COPY whisper_server.py /app/whisper_server.py
WORKDIR /app
CMD ["uvicorn", "whisper_server:app", "--host", "0.0.0.0", "--port", "5001"]
