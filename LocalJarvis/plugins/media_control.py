import importlib.util
import logging
import os

logger = logging.getLogger(__name__)

# Import dinâmico de system_control
system_control_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../command_execution/system_control.py'))
spec = importlib.util.spec_from_file_location('system_control', system_control_path)
system_control = importlib.util.module_from_spec(spec)
spec.loader.exec_module(system_control)

# Import dinâmico de BasePlugin
plugin_template_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'plugin_template.py'))
spec2 = importlib.util.spec_from_file_location('plugin_template', plugin_template_path)
plugin_template = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(plugin_template)
BasePlugin = plugin_template.BasePlugin

class MediaControlPlugin(BasePlugin):
    """Plugin para controle de mídia."""
    
    def __init__(self, config=None):
        super().__init__(config)
        self.control = system_control.SystemControl()
    
    def can_handle(self, text):
        """Verifica se o plugin pode lidar com a entrada."""
        return "play" in text.lower() or "pause" in text.lower()
    
    def handle(self, text):
        """Executa ação de controle de mídia."""
        logger.info(f"Executando ação de mídia para: {text}")
        return self.control.play_pause_media()
