import requests
import logging

logger = logging.getLogger(__name__)

class Plugin:
    """Plugin para consulta de clima (exemplo, desativado)."""
    
    def __init__(self, config):
        self.api_key = config.get('api_key', '')
    
    def can_handle(self, text):
        """Verifica se o plugin pode lidar com a entrada."""
        return "clima" in text.lower()
    
    def handle(self, text):
        """Retorna mensagem de exemplo (API não configurada)."""
        logger.info(f"Tentativa de consultar clima: {text}")
        return "Plugin de clima não configurado. Adicione uma chave API válida."
