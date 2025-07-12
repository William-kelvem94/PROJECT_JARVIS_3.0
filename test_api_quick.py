#!/usr/bin/env python3
"""
🧪 Teste Rápido da API do JARVIS 3.0
"""

import requests
import json

def test_jarvis_api():
    """Testa a API do JARVIS"""
    print("🧪 Testando API do JARVIS 3.0...")
    
    # Endpoint da API
    url = "http://localhost:5000/api/chat"
    
    # Mensagens de teste
    test_messages = [
        {"message": "Olá JARVIS! Como você está?", "personality": "assistente"},
        {"message": "Me conte uma curiosidade interessante", "personality": "amigavel"},
        {"message": "Explique como funciona o Docker", "personality": "tecnico"}
    ]
    
    for i, data in enumerate(test_messages, 1):
        print(f"\n{i}. Testando personalidade: {data['personality']}")
        print(f"   Pergunta: {data['message']}")
        
        try:
            response = requests.post(
                url, 
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Resposta: {result['response'][:100]}...")
                print(f"   🎭 Personalidade: {result['personality']}")
                print(f"   🧠 Modelo: {result['model']}")
            else:
                print(f"   ❌ Erro {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Erro na requisição: {e}")

def test_status_api():
    """Testa API de status"""
    print("\n📊 Testando API de Status...")
    
    try:
        response = requests.get("http://localhost:5000/api/status", timeout=10)
        
        if response.status_code == 200:
            status = response.json()
            print(f"   ✅ Ollama Online: {status['ollama_online']}")
            print(f"   📋 Modelos: {status['models_available']}")
            print(f"   🧠 AI Engine: {status['ai_engine_ready']}")
        else:
            print(f"   ❌ Erro {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")

def test_interface():
    """Testa se a interface está respondendo"""
    print("\n🌐 Testando Interface Web...")
    
    endpoints = [
        ("Interface JARVIS", "http://localhost:5000"),
        ("API Status", "http://localhost:5000/api/status"),
        ("Open WebUI", "http://localhost:3000"),
        ("Jupyter", "http://localhost:8888"),
        ("Ollama API", "http://localhost:11434/api/tags")
    ]
    
    for name, url in endpoints:
        try:
            response = requests.get(url, timeout=5)
            status = "✅ Online" if response.status_code == 200 else f"⚠️ Status {response.status_code}"
            print(f"   • {name}: {status}")
        except Exception as e:
            print(f"   • {name}: ❌ Offline ({str(e)[:50]}...)")

if __name__ == "__main__":
    print("🧠 TESTE COMPLETO DO JARVIS 3.0 - IA LOCAL")
    print("=" * 50)
    
    test_interface()
    test_status_api()
    test_jarvis_api()
    
    print(f"\n" + "=" * 50)
    print("🎉 TESTE CONCLUÍDO!")
    print("🌐 Acesse: http://localhost:5000 para usar a interface")
