import importlib
import logging
import os

logger = logging.getLogger(__name__)

def load_plugins(config):
    """Carrega plugins configurados, incluindo advanced_plugins. Instancia corretamente a classe principal."""
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
                        # Tenta encontrar a classe principal do plugin
                        plugin_class = None
                        if hasattr(module, 'Plugin'):
                            plugin_class = getattr(module, 'Plugin')
                        else:
                            # Procura por classe com nome <NomePlugin> ou <NamePlugin>
                            for attr in dir(module):
                                if attr.lower() == f"{name.lower()}plugin":
                                    plugin_class = getattr(module, attr)
                                    break
                        if plugin_class:
                            plugins[name] = plugin_class(settings)
                        else:
                            logger.warning(f"Plugin {name} não possui classe Plugin ou <Nome>Plugin.")
                        # Checa requirements.txt do plugin
                        req_path = os.path.join(dir_path, name + "_requirements.txt")
                        if os.path.exists(req_path):
                            logger.info(f"Plugin {name} requer dependências extras: {req_path}")
                        logger.info(f"Plugin {name} ({plugin_dir}) carregado.")
                    except Exception as e:
                        logger.error(f"Erro ao carregar plugin {name} de {plugin_dir}: {e}")
    return plugins
