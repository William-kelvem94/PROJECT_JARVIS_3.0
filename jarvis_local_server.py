#!/usr/bin/env python3
"""
🧠 Servidor Web para Interface IA Local do Jarvis 3.0
Serve interface HTML e conecta com Ollama local
"""

from flask import Flask, request, jsonify, render_template_string
import asyncio
import json
import sys
import os
import time
from pathlib import Path

# Add project path
sys.path.append('NEW_JARVIS')

from core.ai_engine import AIEngine
from core.config import Config
from core.ollama_integration import OllamaLocalAI

app = Flask(__name__)

# Global AI engine
ai_engine = None
ollama = None

def init_ai():
    """Inicializa o motor de IA"""
    global ai_engine, ollama
    try:
        config = Config()
        ai_engine = AIEngine(config.ai)
        ollama = OllamaLocalAI()
        print("✅ IA Engine inicializado")
        return True
    except Exception as e:
        print(f"❌ Erro inicializando IA: {e}")
        return False

@app.route('/')
def index():
    """Página principal - Interface Avançada JARVIS"""
    try:
        with open('jarvis_advanced_ai_interface.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        try:
            # Fallback para interface avançada anterior
            with open('jarvis_advanced_interface.html', 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            try:
                # Fallback para interface simples
                with open('jarvis_ai_local_interface.html', 'r', encoding='utf-8') as f:
                    return f.read()
            except FileNotFoundError:
                return """
                <h1>❌ Interface não encontrada</h1>
                <p>Arquivos de interface não estão disponíveis.</p>
                <p>Execute o script de setup primeiro.</p>
                """

@app.route('/api/chat', methods=['POST'])
def chat_api():
    """API endpoint para chat"""
    global ai_engine
    
    try:
        data = request.get_json()
        message = data.get('message', '')
        personality = data.get('personality', 'assistente')
        model = data.get('model', 'jarvis-personal')
        
        if not message:
            return jsonify({'error': 'Mensagem vazia'}), 400
        
        if not ai_engine:
            init_ai()
        
        if not ai_engine:
            return jsonify({'error': 'IA Engine não disponível'}), 500
        
        # Set personality
        ai_engine.set_personality(personality)
        
        # Try to set specific model if provided
        if model and model != 'jarvis-personal':
            try:
                # Update model in ollama integration
                if ai_engine.ollama:
                    ai_engine.ollama.set_model(model)
                    # Update personality mapping
                    ai_engine.personalities[personality]['ollama_model'] = model
            except Exception as e:
                print(f"⚠️ Erro definindo modelo {model}: {e}")
        
        # Get response using asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            response = loop.run_until_complete(ai_engine.chat(message))
        finally:
            loop.close()
        
        return jsonify({
            'success': True,
            'response': response,
            'personality': personality,
            'model': model,
            'timestamp': time.time()
        })
        
    except Exception as e:
        print(f"❌ Erro no chat API: {e}")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route('/api/status')
def status_api():
    """API endpoint para status do sistema"""
    global ai_engine, ollama
    
    try:
        if not ollama:
            ollama = OllamaLocalAI()
        
        # Check Ollama connection
        ollama_status = ollama.check_connection()
        models = ollama.list_models() if ollama_status else []
        
        # Check AI Engine
        if not ai_engine:
            init_ai()
        
        ai_status = ai_engine.get_ai_status() if ai_engine else {}
        
        return jsonify({
            'success': True,
            'ollama_online': ollama_status,
            'models_available': [m['name'] for m in models] if models else [],
            'models_count': len(models) if models else 0,
            'ai_engine_ready': ai_engine is not None,
            'ai_status': ai_status,
            'endpoints': {
                'ollama': 'http://localhost:11434',
                'webui': 'http://localhost:3000', 
                'jupyter': 'http://localhost:8888'
            },
            'timestamp': time.time()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/personalities')
def personalities_api():
    """API endpoint para listar personalidades"""
    global ai_engine
    
    try:
        if not ai_engine:
            init_ai()
        
        if ai_engine:
            return jsonify(ai_engine.personalities)
        else:
            return jsonify({'error': 'AI Engine não disponível'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/models')
def models_api():
    """API endpoint para listar modelos"""
    global ollama
    
    try:
        if not ollama:
            ollama = OllamaLocalAI()
        
        if ollama.check_connection():
            models = ollama.list_models()
            return jsonify({
                'success': True,
                'models': models,
                'current_model': ollama.current_model if hasattr(ollama, 'current_model') else 'jarvis-personal'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Ollama não disponível',
                'models': []
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'models': []
        }), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'service': 'Jarvis 3.0 AI Local Interface',
        'version': '3.0.0'
    })

if __name__ == '__main__':
    print("🧠 JARVIS 3.0 - Interface IA Local")
    print("=" * 50)
    
    # Initialize AI
    if init_ai():
        print("✅ Sistema inicializado com sucesso!")
    else:
        print("⚠️ Sistema iniciado com limitações")
    
    print("\n📡 Endpoints disponíveis:")
    print("• Interface: http://localhost:5000")
    print("• API Chat: http://localhost:5000/api/chat")
    print("• Status: http://localhost:5000/api/status")
    print("• WebUI: http://localhost:3000")
    print("• Jupyter: http://localhost:8888")
    print("• Ollama: http://localhost:11434")
    
    print(f"\n🚀 Iniciando servidor...")
    
    try:
        app.run(
            host='0.0.0.0',
            port=5000, 
            debug=False,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 Servidor finalizado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro no servidor: {e}")
