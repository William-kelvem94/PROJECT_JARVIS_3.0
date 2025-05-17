from command_execution.system_control import SystemControl
import logging

logger = logging.getLogger(__name__)

class Plugin:
    """Plugin para controle de mídia."""
    
    def __init__(self, config):
        self.control = SystemControl()
    
    def can_handle(self, text):
        """Verifica se o plugin pode lidar com a entrada."""
        return "play" in text.lower() or "pause" in text.lower()
    
    def handle(self, text):
        """Executa ação de controle de mídia."""
        logger.info(f"Executando ação de mídia para: {text}")
        return self.control.play_pause_media()
