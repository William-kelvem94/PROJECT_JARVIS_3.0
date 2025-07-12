#!/usr/bin/env python3
"""
🚀 Script de Inicialização Simples do JARVIS 3.0
- Serve a interface web avançada
- Conecta com Ollama (se disponível)
- Não trava ou executa comandos desnecessários
"""

from flask import Flask, request, jsonify
import json
import time
import requests

app = Flask(__name__)

# Estado global
system_status = {
    'ollama_online': False,
    'models': [],
    'current_model': 'llama3.2:1b',
    'uptime_start': time.time()
}

def check_ollama():
    """Verifica se Ollama está online"""
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            data = response.json()
            system_status['ollama_online'] = True
            system_status['models'] = data.get('models', [])
            return True
    except:
        pass
    
    system_status['ollama_online'] = False
    system_status['models'] = []
    return False

@app.route('/')
def index():
    """Serve a interface JARVIS avançada"""
    try:
        with open('jarvis_advanced_ai_interface.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return """
        <h1>❌ Interface não encontrada</h1>
        <p>O arquivo jarvis_advanced_ai_interface.html não foi encontrado.</p>
        <p>Certifique-se de que está executando do diretório correto.</p>
        """

@app.route('/api/models')
def api_models():
    """Lista modelos disponíveis"""
    check_ollama()
    
    # Modelos padrão que esperamos
    default_models = [
        {'name': 'llama3.2:1b', 'size': 1400000000, 'modified_at': '2025-06-29T00:00:00Z'},
        {'name': 'jarvis-personal', 'size': 1400000000, 'modified_at': '2025-06-29T00:00:00Z'},
        {'name': 'mistral', 'size': 4100000000, 'modified_at': '2025-06-29T00:00:00Z'},
        {'name': 'deepseek-coder', 'size': 3800000000, 'modified_at': '2025-06-29T00:00:00Z'}
    ]
    
    # Se Ollama está online, use os modelos reais, senão use os padrão
    models = system_status['models'] if system_status['ollama_online'] else default_models
    
    return jsonify({
        'success': True,
        'models': models,
        'current_model': system_status['current_model']
    })

@app.route('/api/status')
def api_status():
    """Status do sistema"""
    check_ollama()
    
    uptime = int(time.time() - system_status['uptime_start'])
    
    return jsonify({
        'success': True,
        'ollama_online': system_status['ollama_online'],
        'models_available': [m.get('name', 'unknown') for m in system_status['models']],
        'models_count': len(system_status['models']),
        'uptime_seconds': uptime,
        'endpoints': {
            'ollama': 'http://localhost:11434',
            'webui': 'http://localhost:3000',
            'jupyter': 'http://localhost:8888'
        }
    })

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """Endpoint de chat"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        model = data.get('model', system_status['current_model'])
        personality = data.get('personality', 'assistente')
        
        if not message:
            return jsonify({'error': 'Mensagem vazia'}), 400
        
        # Verificar se Ollama está disponível
        if not check_ollama():
            return jsonify({
                'success': True,
                'response': f"🔴 Ollama offline. Sua mensagem foi: '{message}'\n\n💡 Para usar a IA local:\n1. Verifique se o container está rodando: `docker ps`\n2. Se não estiver, inicie: `docker run -d -p 11434:11434 --name Ollama_IA_LOCAL ollama/ollama`\n3. Baixe um modelo: `docker exec Ollama_IA_LOCAL ollama pull llama3.2:1b`",
                'model': 'system',
                'personality': personality
            })
        
        # Tentar comunicar com Ollama
        try:
            response = requests.post('http://localhost:11434/api/generate', 
                json={
                    'model': model,
                    'prompt': f"Você é JARVIS, assistente do Will. Personalidade: {personality}. Responda: {message}",
                    'stream': False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get('response', 'Resposta não disponível')
                
                return jsonify({
                    'success': True,
                    'response': ai_response,
                    'model': model,
                    'personality': personality
                })
            else:
                return jsonify({
                    'success': True,
                    'response': f"❌ Erro do Ollama (status {response.status_code}). Modelo '{model}' pode não estar disponível.\n\nTente baixar: `docker exec Ollama_IA_LOCAL ollama pull {model}`",
                    'model': 'system',
                    'personality': personality
                })
                
        except requests.exceptions.Timeout:
            return jsonify({
                'success': True,
                'response': f"⏱️ Timeout ao processar com modelo '{model}'. O modelo pode estar carregando...\n\nTente novamente em alguns segundos ou use um modelo menor como 'llama3.2:1b'.",
                'model': 'system',
                'personality': personality
            })
        except Exception as e:
            return jsonify({
                'success': True,
                'response': f"❌ Erro na comunicação: {str(e)}\n\nVerifique se o Ollama está funcionando: `docker logs Ollama_IA_LOCAL`",
                'model': 'system',
                'personality': personality
            })
            
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route('/health')
def health():
    """Health check"""
    return jsonify({'status': 'ok', 'service': 'JARVIS 3.0'})

if __name__ == '__main__':
    print("🧠 JARVIS 3.0 - Interface IA Local")
    print("=" * 50)
    print("✅ Servidor simplificado iniciado!")
    print(f"📱 Interface: http://localhost:5000")
    print(f"🔍 Status: http://localhost:5000/api/status")
    print("\n🚀 Pressione Ctrl+C para parar")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n👋 Servidor parado!")
