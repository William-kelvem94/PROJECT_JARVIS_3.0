import importlib
import os
import sys
from typing import Dict, Any

class PluginManager:
    def __init__(self, plugins_dir='plugins'):
        self.plugins_dir = plugins_dir
        self.plugins = {}

    def load_plugins(self):
        sys.path.insert(0, self.plugins_dir)
        for file in os.listdir(self.plugins_dir):
            if file.endswith('.py') and not file.startswith('__'):
                module_name = file[:-3]
                module = importlib.import_module(module_name)
                self.plugins[module_name] = module

    def get_plugin(self, name: str) -> Any:
        return self.plugins.get(name)

# Exemplo de uso:
# pm = PluginManager()
# pm.load_plugins()
# plugin = pm.get_plugin('weather_plugin')
