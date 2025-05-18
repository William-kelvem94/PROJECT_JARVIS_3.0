# Dockerfile otimizado para suporte a GPU, TTS offline, plugins e dependências modernas
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Instala dependências de sistema para pyttsx3, TTS offline e utilitários
RUN apt-get update && \
    apt-get install -y build-essential espeak ffmpeg libasound2 libespeak1 libglib2.0-0 python3-dev python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Copia requirements
COPY requirements.txt .
# Instala torch com CUDA 11.8 do repositório oficial do PyTorch
RUN pip3 install --upgrade pip && \
    pip3 install torch==2.1.0+cu118 --extra-index-url https://download.pytorch.org/whl/cu118 && \
    pip3 install --no-cache-dir -r requirements.txt

# Copia o restante do código
COPY . .

CMD ["python3", "jarvis_entrypoint.py"]
