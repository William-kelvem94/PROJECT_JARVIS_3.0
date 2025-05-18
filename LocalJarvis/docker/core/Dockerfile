# Dockerfile otimizado para CPU/WSL, sem dependências de CUDA/nvidia
FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Instala dependências de sistema para pyttsx3, TTS offline e utilitários
RUN apt-get update && \
    apt-get install -y build-essential espeak ffmpeg libasound2 libespeak1 libglib2.0-0 python3-dev python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Copia requirements
COPY requirements.txt .
RUN pip3 install --upgrade pip && \
    pip3 install --no-cache-dir "numpy<2" && \
    pip3 install --no-cache-dir torch==2.0.1 && \
    pip3 install --no-cache-dir -r requirements.txt

# Copia o restante do código
COPY . .

CMD ["python3", "jarvis_entrypoint.py"]
