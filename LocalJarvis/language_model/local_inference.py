import logging
from transformers import pipeline
import subprocess

logger = logging.getLogger(__name__)

class LocalInference:
    """Classe para inferência com modelos de linguagem locais."""
    
    def __init__(self, model_path, max_tokens=512, use_llama=False):
        self.model_path = model_path
        self.max_tokens = max_tokens
        self.use_llama = use_llama
        if use_llama:
            self.model = None
            logger.info("Usando LLaMA via llama.cpp.")
        else:
            try:
                self.model = pipeline("text-generation", model=model_path)
                logger.info(f"Modelo {model_path} carregado.")
            except Exception as e:
                logger.error(f"Erro ao carregar modelo: {e}")
                self.model = None

    def infer(self, text, context):
        """Gera resposta e detecta ação com base na entrada e contexto."""
        try:
            if self.use_llama:
                prompt = f"{context}\nUsuário: {text}\nAssistente: "
                result = subprocess.run(
                    ["llama.cpp", "--model", self.model_path, "--prompt", prompt, "--max-tokens", str(self.max_tokens)],
                    capture_output=True, text=True
                )
                response = result.stdout
                action = None
                if "abrir" in response.lower():
                    action = response.split('abrir ')[-1].split(' ')[0]
                # Fallback amigável
                if not response.strip() or response.strip() == prompt.strip():
                    response = "Desculpe, não entendi. Pode repetir de outra forma?"
                return response, action

            if not self.model:
                logger.warning("Modelo não carregado. Usando resposta padrão.")
                if "abrir" in text.lower():
                    return f"Ok, abrindo {text.split('abrir ')[-1]}", text.split('abrir ')[-1]
                return f"Você disse: {text}", None

            prompt = f"{context}\nUsuário: {text}\nAssistente: "
            response = self.model(prompt, max_length=self.max_tokens, num_return_sequences=1)[0]['generated_text']
            action = None
            if "abrir" in response.lower():
                action = response.split('abrir ')[-1].split(' ')[0]
            # Fallback amigável
            if not response.strip() or response.strip() == prompt.strip():
                response = "Desculpe, não entendi. Pode repetir de outra forma?"
            logger.info(f"Resposta gerada: {response[:50]}...")
            return response, action
        except Exception as e:
            logger.error(f"Erro na inferência: {e}")
            return f"Erro: {str(e)}", None
