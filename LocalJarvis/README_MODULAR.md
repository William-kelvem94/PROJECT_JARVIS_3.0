# LocalJarvis - Estrutura Modular

## Como funciona

- O núcleo (core) gerencia plugins, mensagens internas e perfis de personalidade.
- Plugins são carregados dinamicamente e podem ter dependências próprias (requirements.txt).
- O sistema de mensagens permite comunicação entre módulos de forma desacoplada.
- Perfis de personalidade podem ser trocados em tempo real.

## Como expandir

1. Adicione plugins em `plugins/`.
2. Cada plugin pode ter seu próprio `requirements.txt`.
3. Use o `PluginManager` para carregar e acessar plugins.
4. Use o `MessageBus` para comunicação entre módulos.
5. Edite `config/personalities.json` para novos perfis.

## Exemplo de inicialização

```python
from core.plugin_manager import PluginManager
from core.message_bus import MessageBus
from core.personality import PersonalityManager

pm = PluginManager()
pm.load_plugins()
bus = MessageBus()
bus.start()
personality = PersonalityManager()
```

## Próximos passos
- Implemente os módulos de NLP, visão computacional, áudio, automação, etc., seguindo a mesma lógica modular.
