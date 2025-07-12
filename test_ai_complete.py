#!/usr/bin/env python3
"""
🧠 Teste Completo da Integração IA Local do Jarvis 3.0
Valida Ollama, WebUI, e integração Python
"""

import asyncio
import sys
import os
sys.path.append('NEW_JARVIS')

from core.ai_engine import AIEngine
from core.config import Config
from core.ollama_integration import OllamaLocalAI

def test_ollama_direct():
    """Teste direto da integração Ollama"""
    print("🔍 Testando Ollama Direct...")
    
    ollama = OllamaLocalAI()
    
    # Verificar conexão
    if not ollama.check_connection():
        print("❌ Ollama não está rodando!")
        return False
    
    print("✅ Ollama conectado!")
    
    # Listar modelos
    models = ollama.list_models()
    print(f"📋 Modelos disponíveis: {len(models)}")
    for model in models:
        print(f"   • {model['name']} ({model.get('size', 'N/A')})")
    
    # Testar com modelo personalizado
    if ollama.set_model("jarvis-personal"):
        print("🎯 Usando modelo personalizado Jarvis")
    else:
        print("⚠️ Modelo personalizado não encontrado, usando padrão")
        ollama.set_model("llama3.2:1b")
    
    # Teste de conversa
    print("\n💬 Teste de Conversa:")
    test_messages = [
        "Olá! Você é o Jarvis?",
        "Qual é o status do sistema?",
        "Me fale sobre suas capacidades"
    ]
    
    for msg in test_messages:
        print(f"\n👤 Usuário: {msg}")
        response = ollama.chat(msg)
        print(f"🤖 Jarvis: {response}")
    
    return True

async def test_ai_engine():
    """Teste do motor de IA completo"""
    print("\n🎯 Testando AI Engine...")
    
    # Configuração básica
    config = Config()
    ai_engine = AIEngine(config.ai)
    
    # Status da IA
    status = ai_engine.get_ai_status()
    print(f"📊 Status IA:")
    print(f"   • Ollama: {'✅' if status['ollama_available'] else '❌'}")
    print(f"   • OpenAI: {'✅' if status['openai_available'] else '❌'}")
    print(f"   • Modo atual: {status['current_mode']}")
    print(f"   • Modelo atual: {status['current_model']}")
    
    # Teste de personalidades
    print(f"\n🎭 Testando Personalidades:")
    personalities = ["assistente", "amigavel", "tecnico"]
    
    for personality in personalities:
        ai_engine.set_personality(personality)
        response = await ai_engine.chat("Apresente-se brevemente")
        print(f"   • {personality}: {response[:100]}...")
    
    # Teste de comandos com contexto
    print(f"\n🔧 Teste com Contexto do Sistema:")
    
    # Simular contexto do sistema
    system_context = {
        "cpu_usage": 45.2,
        "memory_usage": 68.1,
        "uptime": "2 horas, 15 minutos",
        "active_processes": 156
    }
    
    response = await ai_engine.chat(
        "Analise o desempenho atual do sistema", 
        context=system_context
    )
    print(f"🤖 Análise: {response}")
    
    return True

def test_web_access():
    """Testa acesso às interfaces web"""
    print("\n🌐 Testando Interfaces Web...")
    
    import requests
    
    endpoints = [
        ("Ollama API", "http://localhost:11434/api/tags"),
        ("Open WebUI", "http://localhost:3000"),
        ("Jupyter", "http://localhost:8888")
    ]
    
    for name, url in endpoints:
        try:
            response = requests.get(url, timeout=5)
            status = "✅" if response.status_code == 200 else f"⚠️ ({response.status_code})"
            print(f"   • {name}: {status}")
        except Exception as e:
            print(f"   • {name}: ❌ {str(e)}")

def create_quick_demo():
    """Cria demonstração rápida do sistema"""
    print("\n🎬 Criando Demo Interativo...")
    
    demo_content = """
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
"""
    
    with open("AI_LOCAL_DEMO.md", "w", encoding="utf-8") as f:
        f.write(demo_content)
    
    print("✅ Demo criado: AI_LOCAL_DEMO.md")

async def main():
    """Função principal de teste"""
    print("🧠 JARVIS 3.0 - Teste Completo da IA Local\n")
    print("=" * 50)
    
    # Testes sequenciais
    if not test_ollama_direct():
        print("❌ Falha no teste do Ollama")
        return
    
    if not await test_ai_engine():
        print("❌ Falha no teste do AI Engine")
        return
    
    test_web_access()
    create_quick_demo()
    
    print("\n" + "=" * 50)
    print("🎉 TODOS OS TESTES CONCLUÍDOS!")
    print("\n📖 Consulte AI_LOCAL_DEMO.md para exemplos de uso")
    print("🌐 WebUI: http://localhost:3000")
    print("📊 Jupyter: http://localhost:8888 (token: jarvis2025)")

if __name__ == "__main__":
    asyncio.run(main())
