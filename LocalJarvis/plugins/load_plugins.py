import importlib
import logging

logger = logging.getLogger(__name__)

def load_plugins(config):
    """Carrega plugins configurados."""
    plugins = {}
    for name, settings in config.items():
        if settings.get('enabled', False):
            try:
                module = importlib.import_module(f"plugins.{name}")
                plugins[name] = module.Plugin(settings)
                logger.info(f"Plugin {name} carregado.")
            except Exception as e:
                logger.error(f"Erro ao carregar plugin {name}: {e}")
    return plugins
