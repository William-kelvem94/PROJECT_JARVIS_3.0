# Script para forçar o download do modelo gpt2 ao buildar o container
from transformers import pipeline

def download_gpt2():
    print("Baixando modelo gpt2...")
    pipe = pipeline("text-generation", model="gpt2")
    print("Modelo gpt2 baixado com sucesso.")

if __name__ == "__main__":
    download_gpt2()
