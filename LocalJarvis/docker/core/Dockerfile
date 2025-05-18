# Dockerfile otimizado para CPU/WSL, sem dependências de CUDA/nvidia
FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Instala dependências de sistema para pyttsx3, TTS offline e utilitários
RUN apt-get update && \
    apt-get install -y build-essential espeak ffmpeg libasound2 libespeak1 libglib2.0-0 python3-dev python3-pip curl && \
    rm -rf /var/lib/apt/lists/*

# Copia requirements
COPY requirements.txt .
RUN pip3 install --upgrade pip && \
    pip3 install --no-cache-dir "numpy<2"

# Instala torch via wheel oficial (mais robusto para Docker)
RUN echo "Instalando torch via wheel oficial..." && \
    curl -sSL -o torch-2.0.1-cp310-cp310-linux_x86_64.whl https://download.pytorch.org/whl/cpu/torch-2.0.1%2Bcpu-cp310-cp310-linux_x86_64.whl && \
    pip3 install --no-cache-dir torch-2.0.1-cp310-cp310-linux_x86_64.whl || \
    (echo "Falha no wheel, tentando via PyPI..." && pip3 install --no-cache-dir torch==2.0.1 --index-url https://pypi.org/simple)

RUN pip3 install --no-cache-dir -r requirements.txt

# Copia o restante do código
COPY . .

CMD ["python3", "jarvis_entrypoint.py"]
