
# 🧠 Jarvis 3.0 - IA Local Demo

## 🚀 Endpoints Disponíveis:
- **WebUI**: http://localhost:3000 (Interface tipo ChatGPT)
- **Jupyter**: http://localhost:8888 (token: jarvis2025)
- **Ollama API**: http://localhost:11434

## 🎯 Modelos Disponíveis:
- `jarvis-personal` - Modelo personalizado do Jarvis
- `llama3.2:1b` - Modelo base Llama

## 💡 Exemplos de Uso:

### Via WebUI (Recomendado):
1. Abra http://localhost:3000
2. Faça login/cadastro
3. Selecione modelo "jarvis-personal"
4. Comece a conversar!

### Via Python:
```python
from core.ai_engine import AIEngine
from core.config import Config

config = Config()
ai = AIEngine(config.ai)

# Conversa simples
response = await ai.chat("Olá Jarvis!")
print(response)

# Com contexto do sistema
context = {"cpu_usage": 45.2, "memory_usage": 68.1}
response = await ai.chat("Como está o sistema?", context=context)
print(response)
```

### Via API direta:
```bash
curl -X POST http://localhost:11434/api/generate -d '{
  "model": "jarvis-personal",
  "prompt": "Olá! Você é o Jarvis?",
  "stream": false
}'
```

## 🎭 Personalidades:
- **assistente**: Formal e profissional
- **amigavel**: Descontraído e casual  
- **tecnico**: Especialista em tecnologia

## 🔧 Comandos Úteis:
```bash
# Status containers
docker ps

# Logs do Ollama
docker logs Ollama_IA_LOCAL

# Modelos disponíveis
docker exec Ollama_IA_LOCAL ollama list

# Conversa via terminal
docker exec -it Ollama_IA_LOCAL ollama run jarvis-personal
```
