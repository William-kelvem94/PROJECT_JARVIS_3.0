#!/usr/bin/env python3
"""
Servidor Flask simples para testar a interface Jarvis 3.0
"""
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
import os
import json
from datetime import datetime

# Configuração correta do Flask para servir arquivos estáticos
app = Flask(__name__, 
            static_folder='frontend',
            static_url_path='')
CORS(app)

# Simula dados para a interface
fake_metrics = {
    "cpuUsage": "28%",
    "memoryUsage": "64%", 
    "activePlugins": 8,
    "requestsProcessed": 142,
    "uptime": 3600,
    "networkStatus": "Connected"
}

fake_plugins = [
    {"id": "assistant", "name": "Assistant AI", "status": "active", "enabled": True, "description": "Plugin principal de assistente inteligente"},
    {"id": "vision", "name": "Computer Vision", "status": "active", "enabled": True, "description": "Análise de imagem e reconhecimento de objetos"},
    {"id": "security", "name": "Security Monitor", "status": "active", "enabled": True, "description": "Monitoramento de segurança em tempo real"},
    {"id": "weather", "name": "Weather Info", "status": "idle", "enabled": True, "description": "Informações meteorológicas atualizadas"},
    {"id": "automation", "name": "Home Automation", "status": "idle", "enabled": False, "description": "Controle de dispositivos domésticos"},
    {"id": "games", "name": "Entertainment", "status": "idle", "enabled": True, "description": "Jogos e entretenimento interativo"},
    {"id": "education", "name": "Learning Hub", "status": "idle", "enabled": True, "description": "Recursos educacionais e tutoriais"},
    {"id": "data", "name": "Data Analytics", "status": "active", "enabled": True, "description": "Análise de dados e relatórios"}
]

@app.route('/')
def index():
    """Serve a interface principal"""
    try:
        return send_from_directory('frontend', 'index.html')
    except Exception as e:
        return f"Erro ao carregar interface: {e}"

@app.route('/style.css')
def styles():
    """Serve o arquivo CSS"""
    return send_from_directory('frontend', 'style.css')

@app.route('/app.js')
def app_js():
    """Serve o arquivo JavaScript"""
    return send_from_directory('frontend', 'app.js')

@app.route('/chat.js')
def chat_js():
    """Serve o arquivo de chat"""
    return send_from_directory('frontend', 'chat.js')

@app.route('/<path:filename>')
def static_files(filename):
    """Serve arquivos estáticos"""
    try:
        return send_from_directory('frontend', filename)
    except Exception as e:
        return f"Arquivo não encontrado: {filename}"

@app.route('/api/chat', methods=['POST'])
def chat():
    """Endpoint para chat com o Jarvis"""
    data = request.get_json()
    message = data.get('message', '')
    
    # Simula respostas do Jarvis baseadas na mensagem
    responses = {
        'oi': '🤖 Olá! Sou o Jarvis 3.0, seu assistente futurístico! Como posso ajudá-lo hoje?',
        'como está': '✅ Todos os sistemas funcionando perfeitamente! Interface futurística carregada com sucesso.',
        'plugins': f'📋 Tenho {len([p for p in fake_plugins if p["enabled"]])} plugins ativos: ' + ', '.join([p["name"] for p in fake_plugins if p["enabled"]]),
        'status': '🟢 Status: Online | CPU: 28% | RAM: 64% | Plugins: 8 ativos',
        'visão': '👁️ Sistema de visão computacional ativo! Posso analisar imagens e detectar objetos.',
        'segurança': '🔒 Sistema de segurança monitorando. Nenhuma ameaça detectada.',
        'default': '🤖 Interface futurística do Jarvis 3.0 funcionando perfeitamente! Todos os módulos estão online e prontos para uso.'
    }
    
    # Encontra resposta apropriada
    response_text = responses.get('default')
    for key, value in responses.items():
        if key in message.lower():
            response_text = value
            break
    
    return jsonify({
        "response": response_text,
        "timestamp": datetime.now().isoformat(),
        "actions": []
    })

@app.route('/api/metrics')
def metrics():
    """Endpoint para métricas do sistema"""
    return jsonify(fake_metrics)

@app.route('/api/plugins')
def plugins():
    """Endpoint para lista de plugins"""
    return jsonify(fake_plugins)

@app.route('/api/plugins/<plugin_id>/toggle', methods=['POST'])
def toggle_plugin(plugin_id):
    """Toggle de plugins"""
    for plugin in fake_plugins:
        if plugin['id'] == plugin_id:
            plugin['enabled'] = not plugin['enabled']
            plugin['status'] = 'active' if plugin['enabled'] else 'inactive'
            break
    
    return jsonify({"success": True})

@app.route('/api/security/metrics')
def security_metrics():
    """Métricas de segurança"""
    return jsonify({
        "score": 94,
        "threatsBlocked": 23,
        "vulnerabilities": 0,
        "lastScan": datetime.now().isoformat()
    })

@app.route('/api/vision/analyze', methods=['POST'])
def analyze_vision():
    """Análise de imagem (simulada)"""
    return jsonify({
        "objects": [
            {"name": "Pessoa", "confidence": 0.95},
            {"name": "Computador", "confidence": 0.87},
            {"name": "Mesa", "confidence": 0.76}
        ],
        "confidence": 0.86,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload de arquivos (simulado)"""
    files = request.files
    return jsonify({
        "success": True,
        "files_count": len(files),
        "analysis": "Arquivos processados com sucesso pela IA!"
    })

if __name__ == '__main__':
    print("🤖 JARVIS 3.0 - INTERFACE FUTURÍSTICA")
    print("=" * 60)
    print("✅ Servidor Flask iniciado com sucesso!")
    print("🌐 Acesse: http://localhost:5000")
    print("🚀 Interface ultra-futurística carregada!")
    print("🎯 Recursos disponíveis:")
    print("   • Chat AI interativo")
    print("   • Dashboard de métricas em tempo real")
    print("   • Sistema de visão computacional")
    print("   • Monitor de segurança")
    print("   • Gerenciador de plugins")
    print("   • Sistema de treinamento de IA")
    print("   • Analytics avançados")
    print("=" * 60)
    print("💡 Digite mensagens no chat para interagir!")
    print("🔧 Use as abas para navegar pelos módulos!")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
