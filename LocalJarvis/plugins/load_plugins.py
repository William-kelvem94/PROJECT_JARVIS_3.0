import importlib
import logging
import os

logger = logging.getLogger(__name__)

def load_plugins(config):
    """Carrega plugins configurados, incluindo advanced_plugins. Loga dependências se houver requirements.txt."""
    plugins = {}
    plugin_dirs = ["plugins", "advanced_plugins"]
    for plugin_dir in plugin_dirs:
        dir_path = os.path.join(os.path.dirname(__file__), "..", plugin_dir)
        if not os.path.isdir(dir_path):
            continue
        for filename in os.listdir(dir_path):
            if filename.endswith(".py") and not filename.startswith("__"):
                name = filename[:-3]
                settings = config.get(name, {})
                if settings.get('enabled', True):
                    try:
                        module = importlib.import_module(f"{plugin_dir}.{name}")
                        plugins[name] = getattr(module, 'Plugin', None) or getattr(module, name.capitalize() + 'Plugin', None) or module
                        # Checa requirements.txt do plugin
                        req_path = os.path.join(dir_path, name + "_requirements.txt")
                        if os.path.exists(req_path):
                            logger.info(f"Plugin {name} requer dependências extras: {req_path}")
                        logger.info(f"Plugin {name} ({plugin_dir}) carregado.")
                    except Exception as e:
                        logger.error(f"Erro ao carregar plugin {name} de {plugin_dir}: {e}")
    return plugins
