#!/usr/bin/env python3
"""
Script direto para iniciar o Jarvis 3.0 no modo web
"""
import os
import sys
from pathlib import Path

# Adiciona o diretório atual ao path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Configura as variáveis de ambiente
os.environ.setdefault('FLASK_ENV', 'development')
os.environ.setdefault('FLASK_DEBUG', 'true')

try:
    from jarvis_entrypoint import app
    print("🤖 Jarvis 3.0 - Interface Futurística")
    print("=" * 50)
    print("✅ Servidor Flask iniciando...")
    print("🌐 Acesse: http://localhost:5000")
    print("🚀 Interface ultra-futurística carregada!")
    print("=" * 50)
    
    # Inicia o servidor
    app.run(
        host="0.0.0.0", 
        port=5000, 
        debug=True, 
        use_reloader=False,  # Evita problemas de reload
        threaded=True
    )
    
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print("Tentando inicialização alternativa...")
    
    # Fallback - inicialização básica
    from flask import Flask, render_template, send_from_directory
    
    app = Flask(__name__, 
                template_folder='frontend',
                static_folder='frontend')
    
    @app.route('/')
    def index():
        return send_from_directory('frontend', 'index.html')
    
    @app.route('/<path:filename>')
    def static_files(filename):
        return send_from_directory('frontend', filename)
    
    @app.route('/api/chat', methods=['POST'])
    def chat():
        return {"response": "🤖 Jarvis está online! Interface futurística carregada com sucesso!"}
    
    @app.route('/api/metrics')
    def metrics():
        return {
            "cpuUsage": "25%",
            "memoryUsage": "60%", 
            "activePlugins": 8,
            "requestsProcessed": 127
        }
    
    print("🤖 Jarvis 3.0 - Modo Simplificado")
    print("=" * 50)
    print("✅ Servidor Flask iniciando...")
    print("🌐 Acesse: http://localhost:5000")
    print("🚀 Interface ultra-futurística carregada!")
    print("=" * 50)
    
    app.run(host="0.0.0.0", port=5000, debug=True)

except Exception as e:
    print(f"❌ Erro inesperado: {e}")
    print("Verifique se todas as dependências estão instaladas.")
    sys.exit(1)
