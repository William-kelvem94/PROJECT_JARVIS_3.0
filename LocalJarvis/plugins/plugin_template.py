"""
Template para criação de novos plugins do LocalJarvis.
Copie este arquivo e personalize.
"""
import logging
logger = logging.getLogger(__name__)

class Plugin:
    def __init__(self, config):
        self.config = config

    def can_handle(self, text):
        """Retorna True se o plugin pode lidar com o texto."""
        return False

    def handle(self, text):
        """Processa o texto e retorna uma resposta."""
        logger.info(f"Plugin {self.__class__.__name__} chamado com: {text}")
        return "[Stub] Resposta do plugin."

    def process(self, text):
        """Interface alternativa para integração com o núcleo."""
        if self.can_handle(text):
            return self.handle(text)
        return None

    def on_event(self, event):
        """Recebe eventos do núcleo (opcional)."""
        logger.info(f"Evento recebido: {event}")
