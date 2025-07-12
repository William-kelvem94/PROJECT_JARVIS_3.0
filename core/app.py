"""
Aplicação principal do JARVIS 3.0
"""

import asyncio
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import threading
import time
from typing import Optional

from core.config import Config
from core.system_monitor import SystemMonitor
from core.ai_engine import AIEngine
from utils.logger_fixed import default_logger, setup_logger

class JarvisApp:
    """Aplicação principal do JARVIS 3.0"""
    
    def __init__(self, config: Config):
        self.config = config
        from utils.logger_fixed import default_logger
        self.logger = default_logger
        
        # Inicializa componentes
        self.system_monitor = SystemMonitor()
        self.ai_engine = AIEngine(config.ai)
        
        # Configuração do Flask com caminhos absolutos
        import os
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        template_dir = os.path.join(base_dir, 'web', 'templates')
        static_dir = os.path.join(base_dir, 'web', 'static')
        
        self.app = Flask(__name__, 
                        template_folder=template_dir,
                        static_folder=static_dir)
        self.app.secret_key = config.web.secret_key
        
        # CORS
        if config.web.enable_cors:
            CORS(self.app)
        
        # SocketIO para comunicação em tempo real
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Variáveis de controle
        self.monitoring_active = False
        self.monitoring_thread = None
        
        # Registra rotas
        self._register_routes()
        self._register_socket_events()
        
    def _register_routes(self):
        """Registra as rotas da aplicação"""
        
        @self.app.route('/')
        def index():
            """Página principal"""
            return render_template('index.html')
        
        @self.app.route('/dashboard')
        def dashboard():
            """Dashboard de monitoramento"""
            return render_template('dashboard.html')
        
        @self.app.route('/chat')
        def chat():
            """Interface de chat"""
            return render_template('chat.html')
        
        @self.app.route('/ai-control')
        def ai_control():
            """Interface de controle de IA"""
            return render_template('ai_control.html')
        
        @self.app.route('/api/system/info')
        def api_system_info():
            """API: Informações do sistema"""
            try:
                info = self.system_monitor.get_system_info()
                return jsonify({
                    'success': True,
                    'data': {
                        'cpu_percent': info.cpu_percent,
                        'memory_percent': info.memory_percent,
                        'memory_used': info.memory_used,
                        'memory_total': info.memory_total,
                        'disk_percent': info.disk_percent,
                        'disk_used': info.disk_used,
                        'disk_total': info.disk_total,
                        'network_sent': info.network_sent,
                        'network_recv': info.network_recv,
                        'uptime': info.uptime,
                        'temperature': info.temperature,
                        'battery_percent': info.battery_percent,
                        'battery_plugged': info.battery_plugged,
                        'gpu_usage': info.gpu_usage
                    }
                })
            except Exception as e:
                self.logger.error(f"Erro ao obter informações do sistema: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/system/overview')
        def api_system_overview():
            """API: Visão geral do sistema"""
            try:
                overview = self.system_monitor.get_system_overview()
                return jsonify({'success': True, 'data': overview})
            except Exception as e:
                self.logger.error(f"Erro ao obter visão geral: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/chat', methods=['POST'])
        def api_chat():
            """API: Chat com IA"""
            try:
                data = request.get_json()
                message = data.get('message', '')
                
                if not message:
                    return jsonify({'success': False, 'error': 'Mensagem vazia'}), 400
                
                # Processa mensagem de forma assíncrona
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Adiciona contexto do sistema
                system_info = self.system_monitor.get_system_info()
                context = {
                    'cpu_percent': system_info.cpu_percent,
                    'memory_percent': system_info.memory_percent,
                    'battery_percent': system_info.battery_percent
                }
                
                response = loop.run_until_complete(
                    self.ai_engine.chat(message, context)
                )
                loop.close()
                
                return jsonify({
                    'success': True,
                    'response': response,
                    'personality': self.ai_engine.current_personality
                })
                
            except Exception as e:
                self.logger.error(f"Erro no chat: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/ai/personality', methods=['POST'])
        def api_set_personality():
            """API: Define personalidade da IA"""
            try:
                data = request.get_json()
                personality = data.get('personality', '')
                
                self.ai_engine.set_personality(personality)
                
                return jsonify({
                    'success': True,
                    'current_personality': self.ai_engine.current_personality
                })
                
            except Exception as e:
                self.logger.error(f"Erro ao definir personalidade: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/ai/personalities')
        def api_get_personalities():
            """API: Lista personalidades disponíveis"""
            personalities = [
                {
                    'id': key,
                    'name': value['name'],
                    'description': value['description']
                }
                for key, value in self.ai_engine.personalities.items()
            ]
            
            return jsonify({
                'success': True,
                'personalities': personalities,
                'current': self.ai_engine.current_personality
            })
    
    def _register_socket_events(self):
        """Registra eventos do WebSocket"""
        
        @self.socketio.on('connect')
        def handle_connect():
            self.logger.info("Cliente conectado via WebSocket")
            emit('connected', {'status': 'connected'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            self.logger.info("Cliente desconectado via WebSocket")
        
        @self.socketio.on('start_monitoring')
        def handle_start_monitoring():
            """Inicia monitoramento em tempo real"""
            if not self.monitoring_active:
                self.start_monitoring()
                emit('monitoring_started', {'status': 'started'})
        
        @self.socketio.on('stop_monitoring')
        def handle_stop_monitoring():
            """Para monitoramento em tempo real"""
            if self.monitoring_active:
                self.stop_monitoring()
                emit('monitoring_stopped', {'status': 'stopped'})
        
        @self.socketio.on('chat_message')
        def handle_chat_message(data):
            """Processa mensagem de chat via WebSocket"""
            try:
                message = data.get('message', '').strip()
                
                if not message:
                    emit('chat_error', {'error': 'Mensagem vazia'})
                    return
                
                self.logger.info(f"💬 Processando mensagem: {message[:50]}...")
                
                # CORREÇÃO: Processar de forma mais robusta
                try:
                    # Coleta contexto do sistema
                    system_info = self.system_monitor.get_system_info()
                    context = {
                        'cpu_percent': round(system_info.cpu_percent, 1),
                        'memory_percent': round(system_info.memory_percent, 1),
                        'timestamp': time.time()
                    }
                    
                    # Usar thread para não bloquear o WebSocket
                    import threading
                    
                    def process_ai_message():
                        try:
                            # Criar novo loop para a thread
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            
                            response = loop.run_until_complete(
                                self.ai_engine.chat(message, context)
                            )
                            loop.close()
                            
                            # Enviar resposta
                            self.socketio.emit('chat_response', {
                                'message': message,
                                'response': response,
                                'timestamp': time.time()
                            })
                            
                            self.logger.info("✅ Resposta enviada via WebSocket")
                            
                        except Exception as e:
                            self.logger.error(f"Erro processando IA: {e}")
                            self.socketio.emit('chat_error', {
                                'error': 'Erro processando sua mensagem. Tente novamente.'
                            })
                    
                    # Executar em thread separada
                    thread = threading.Thread(target=process_ai_message)
                    thread.daemon = True
                    thread.start()
                    
                except Exception as e:
                    self.logger.error(f"Erro preparando contexto: {e}")
                    emit('chat_error', {'error': 'Erro interno do sistema'})
                
            except Exception as e:
                self.logger.error(f"Erro crítico no WebSocket chat: {e}")
                emit('chat_error', {'error': 'Erro crítico no sistema'})
    
    def start_monitoring(self):
        """Inicia monitoramento de sistema em tempo real"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        self.logger.info("Monitoramento de sistema iniciado")
    
    def stop_monitoring(self):
        """Para monitoramento de sistema"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2)
        
        self.logger.info("Monitoramento de sistema parado")
    
    def _monitoring_loop(self):
        """Loop de monitoramento que envia dados via WebSocket"""
        while self.monitoring_active:
            try:
                # Coleta dados do sistema
                system_info = self.system_monitor.get_system_info()
                
                # Envia via WebSocket apenas para clientes conectados - DADOS LIMITADOS E ARREDONDADOS
                self.socketio.emit('system_update', {
                    'timestamp': time.time(),
                    'cpu_percent': min(round(system_info.cpu_percent, 1), 100),  # Limita a 100%
                    'memory_percent': min(round(system_info.memory_percent, 1), 100),  # Limita a 100%
                    'memory_used': round(system_info.memory_used, 1),
                    'memory_total': round(system_info.memory_total, 1),
                    'disk_percent': min(round(system_info.disk_percent, 1), 100),  # Limita a 100%
                    'network_sent': max(0, min(round(system_info.network_sent, 3), 100)),  # Limita entre 0-100 MB/s
                    'network_recv': max(0, min(round(system_info.network_recv, 3), 100)),  # Limita entre 0-100 MB/s
                    'temperature': round(system_info.temperature, 1) if system_info.temperature else None,
                    'battery_percent': system_info.battery_percent,
                    'battery_plugged': system_info.battery_plugged,
                    'uptime': round(system_info.uptime, 2) if hasattr(system_info, 'uptime') else None
                })
                
                # CORREÇÃO: Intervalo mínimo rigoroso de 3 segundos para evitar sobrecarga
                sleep_time = max(self.config.system.monitoring_interval, 3)
                time.sleep(sleep_time)
                
            except Exception as e:
                self.logger.error(f"Erro no loop de monitoramento: {e}")
                time.sleep(5)  # Aguarda mais tempo em caso de erro
    
    def run_web_server(self, host: str = None, port: int = None, debug: bool = None):
        """Executa o servidor web"""
        host = host or self.config.web.host
        port = port or self.config.web.port
        debug = debug if debug is not None else self.config.web.debug
        
        self.logger.info(f"🌐 Servidor web iniciando em http://{host}:{port}")
        
        # CORREÇÃO: Não inicia monitoramento automaticamente
        # Usuário deve clicar em "Iniciar" no dashboard
        self.logger.info("💡 Clique em 'Iniciar' no dashboard para ativar monitoramento em tempo real")
        
        try:
            # Correção para Python 3.13+ - desabilita reloader se houver erro
            import sys
            if sys.version_info >= (3, 13) and debug:
                self.logger.warning("⚠️ Modo debug desabilitado no Python 3.13+ devido a incompatibilidade do watchdog")
                self.socketio.run(self.app, host=host, port=port, debug=False, use_reloader=False)
            else:
                self.socketio.run(self.app, host=host, port=port, debug=debug)
        except TypeError as e:
            if "'handle' must be a _ThreadHandle" in str(e):
                self.logger.warning("⚠️ Executando sem reloader devido a incompatibilidade do watchdog")
                self.socketio.run(self.app, host=host, port=port, debug=False, use_reloader=False)
            else:
                raise
        except KeyboardInterrupt:
            self.logger.info("Servidor interrompido pelo usuário")
        finally:
            self.stop_monitoring()
    
    def run_cli(self):
        """Executa em modo CLI"""
        self.logger.info("💻 Modo CLI iniciado")
        
        print("🤖 JARVIS 3.0 - Assistente Virtual")
        print("Digite 'sair' para encerrar\n")
        
        while True:
            try:
                user_input = input("Você: ").strip()
                
                if user_input.lower() in ['sair', 'exit', 'quit']:
                    print("👋 Até logo!")
                    break
                
                if not user_input:
                    continue
                
                # Processa comando
                print("🤔 Processando...")
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                system_info = self.system_monitor.get_system_info()
                context = {
                    'cpu_percent': system_info.cpu_percent,
                    'memory_percent': system_info.memory_percent
                }
                
                response = loop.run_until_complete(
                    self.ai_engine.chat(user_input, context)
                )
                loop.close()
                
                print(f"JARVIS: {response}\n")
                
            except KeyboardInterrupt:
                print("\n👋 Sistema encerrado pelo usuário")
                break
            except Exception as e:
                self.logger.error(f"Erro no CLI: {e}")
                print(f"❌ Erro: {e}\n")
