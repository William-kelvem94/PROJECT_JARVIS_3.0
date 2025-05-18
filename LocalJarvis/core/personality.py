import json
import os

class PersonalityManager:
    def __init__(self, config_path='config/personalities.json'):
        self.config_path = config_path
        self.personalities = self.load_personalities()
        self.current = 'default'

    def load_personalities(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'default': {'tone': 'neutro', 'style': 'padrão'}}

    def set_personality(self, name):
        if name in self.personalities:
            self.current = name

    def get_current(self):
        return self.personalities.get(self.current, self.personalities['default'])

# Exemplo de uso:
# pm = PersonalityManager()
# pm.set_personality('descontraido')
# print(pm.get_current())
