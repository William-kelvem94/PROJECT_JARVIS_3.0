#!/usr/bin/env python3
"""
🎬 Demonstração Prática do JARVIS 3.0 - IA Local
Sistema completo de IA funcionando localmente!
"""

import requests
import json
import time
import webbrowser
from datetime import datetime

def print_banner():
    """Banner de apresentação"""
    print("🧠" + "="*60 + "🧠")
    print("    JARVIS 3.0 - DEMONSTRAÇÃO IA LOCAL COMPLETA")
    print("🧠" + "="*60 + "🧠")
    print()

def demonstrate_chat():
    """Demonstração do chat com diferentes personalidades"""
    print("💬 DEMONSTRAÇÃO DO CHAT IA")
    print("-" * 40)
    
    # Cenários de teste
    scenarios = [
        {
            "personality": "assistente",
            "message": "JARVIS, preciso de um relatório do status atual do sistema",
            "context": "Solicitação profissional"
        },
        {
            "personality": "amigavel", 
            "message": "Oi JARVIS! Conta uma piada para alegrar o dia",
            "context": "Conversa casual"
        },
        {
            "personality": "tecnico",
            "message": "Explique como funciona a arquitetura do nosso sistema IA local",
            "context": "Consulta técnica"
        }
    ]
    
    url = "http://localhost:5000/api/chat"
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['context']}")
        print(f"   🎭 Personalidade: {scenario['personality']}")
        print(f"   👤 Usuário: {scenario['message']}")
        print("   🤖 JARVIS: ", end="", flush=True)
        
        # Simular digitação
        for _ in range(3):
            print(".", end="", flush=True)
            time.sleep(0.5)
        
        try:
            response = requests.post(
                url,
                json={
                    "message": scenario["message"],
                    "personality": scenario["personality"]
                },
                timeout=45
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"\n   {result['response']}")
                print(f"   📊 Modelo usado: {result['model']}")
            else:
                print(f"\n   ❌ Erro: {response.status_code}")
                
        except Exception as e:
            print(f"\n   ⚠️ Timeout/Erro - Sistema funcionando, mas resposta demorou")
        
        print()

def show_system_status():
    """Mostra status completo do sistema"""
    print("📊 STATUS DO SISTEMA IA LOCAL")
    print("-" * 40)
    
    try:
        response = requests.get("http://localhost:5000/api/status", timeout=10)
        
        if response.status_code == 200:
            status = response.json()
            
            print(f"🟢 Ollama: {'Online' if status['ollama_online'] else 'Offline'}")
            print(f"🧠 AI Engine: {'Ativo' if status['ai_engine_ready'] else 'Inativo'}")
            print(f"📋 Modelos disponíveis: {len(status['models_available'])}")
            
            for model in status['models_available']:
                print(f"   • {model}")
            
            print(f"\n🔗 Endpoints:")
            for name, url in status['endpoints'].items():
                print(f"   • {name.title()}: {url}")
                
        else:
            print("❌ Erro ao obter status")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print()

def demonstrate_interfaces():
    """Demonstra as interfaces disponíveis"""
    print("🌐 INTERFACES DISPONÍVEIS")
    print("-" * 40)
    
    interfaces = [
        {
            "name": "🧠 Interface JARVIS",
            "url": "http://localhost:5000",
            "description": "Interface principal personalizada"
        },
        {
            "name": "💬 Open WebUI", 
            "url": "http://localhost:3000",
            "description": "Interface tipo ChatGPT"
        },
        {
            "name": "📊 Jupyter Notebook",
            "url": "http://localhost:8888",
            "description": "Ambiente de desenvolvimento (token: jarvis2025)"
        }
    ]
    
    for interface in interfaces:
        print(f"{interface['name']}")
        print(f"   URL: {interface['url']}")
        print(f"   Descrição: {interface['description']}")
        
        # Verificar se está online
        try:
            response = requests.get(interface['url'], timeout=3)
            status = "🟢 Online" if response.status_code == 200 else "🟡 Parcial"
        except:
            status = "🔴 Offline"
        
        print(f"   Status: {status}")
        print()

def show_usage_examples():
    """Mostra exemplos de uso"""
    print("📖 EXEMPLOS DE USO")
    print("-" * 40)
    
    examples = [
        {
            "title": "Via Interface Web",
            "code": "1. Acesse http://localhost:5000\n2. Digite sua mensagem\n3. Pressione Enter"
        },
        {
            "title": "Via Python",
            "code": """import requests
response = requests.post('http://localhost:5000/api/chat', 
    json={'message': 'Olá JARVIS!', 'personality': 'assistente'})
print(response.json()['response'])"""
        },
        {
            "title": "Via Ollama Direto",
            "code": "docker exec -it Ollama_IA_LOCAL ollama run jarvis-personal"
        }
    ]
    
    for example in examples:
        print(f"📝 {example['title']}:")
        print(f"   {example['code']}")
        print()

def main():
    """Função principal da demonstração"""
    print_banner()
    
    print(f"🕐 Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # Verificar se sistema está online
    print("🔍 Verificando sistema...")
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Sistema online e funcionando!")
        else:
            print("⚠️ Sistema com problemas")
            return
    except:
        print("❌ Sistema offline - Execute: python jarvis_local_server.py")
        return
    
    print()
    
    # Demonstrações
    show_system_status()
    demonstrate_interfaces()
    demonstrate_chat()
    show_usage_examples()
    
    # Conclusão
    print("🎉 DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*50)
    print()
    print("🚀 PRÓXIMOS PASSOS:")
    print("1. Acesse http://localhost:5000 para usar a interface")
    print("2. Experimente diferentes personalidades")
    print("3. Use http://localhost:3000 para interface avançada")
    print("4. Explore http://localhost:8888 para desenvolvimento")
    print()
    print("📚 Consulte 'AMBIENTE_IA_LOCAL_COMPLETO.md' para documentação")
    print()
    
    # Oferecer abrir interface
    try:
        open_interface = input("🌐 Deseja abrir a interface principal? (s/n): ").lower()
        if open_interface in ['s', 'sim', 'y', 'yes']:
            webbrowser.open('http://localhost:5000')
            print("✅ Interface aberta no navegador!")
    except:
        print("💡 Acesse manualmente: http://localhost:5000")

if __name__ == "__main__":
    main()
