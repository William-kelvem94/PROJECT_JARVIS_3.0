"""
Sistema de IA do JARVIS 3.0
Suporte para OpenAI e Ollama Local
"""

import openai
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
from utils.logger_fixed import setup_logger
from core.plugins import plugin_manager
from core.ollama_integration import OllamaLocalAI

class AIEngine:
    """Motor de IA principal do JARVIS"""
    
    DEFAULT_OLLAMA_MODEL = "llama3.2:1b"
    
    def __init__(self, ai_config):
        self.config = ai_config
        from utils.logger_fixed import default_logger
        self.logger = default_logger
        
        # Configuração da API OpenAI
        if self.config.api_key:
            openai.api_key = self.config.api_key
        
        # Inicializar Ollama Local
        self.ollama = OllamaLocalAI()
        self.use_local_ai = False
        
        # Verificar se Ollama está disponível
        if self.ollama.check_connection():
            self.use_local_ai = True
            self.logger.info("🧠 Ollama Local AI detectado e ativo!")
            
            # Tentar criar modelo personalizado Jarvis
            self._setup_jarvis_model()
        else:
            self.logger.info("Ollama não detectado. Usando modo API ou fallback.")
        
        # Personalidades disponíveis
        self.personalities = {
            "assistente": {
                "name": "Assistente Profissional",
                "description": "Assistente formal e direto",
                "system_prompt": "Você é JARVIS, um assistente virtual profissional e eficiente. Seja direto, claro e útil.",
                "ollama_model": "jarvis-personal"  # Modelo personalizado
            },
            "amigavel": {
                "name": "Amigável",
                "description": "Assistente descontraído e amigável",
                "system_prompt": "Você é JARVIS, um assistente virtual amigável e descontraído. Use um tom casual e seja prestativo.",
                "ollama_model": self.DEFAULT_OLLAMA_MODEL
            },
            "tecnico": {
                "name": "Técnico",
                "description": "Especialista em tecnologia",
                "system_prompt": "Você é JARVIS, um assistente técnico especializado. Forneça informações detalhadas e precisas sobre tecnologia.",
                "ollama_model": self.DEFAULT_OLLAMA_MODEL
            }
        }
        
        self.current_personality = "assistente"
        self.conversation_history = []
        
    def set_personality(self, personality: str):
        """Define a personalidade da IA"""
        if personality in self.personalities:
            self.current_personality = personality
            self.logger.info(f"Personalidade alterada para: {self.personalities[personality]['name']}")
        else:
            self.logger.warning(f"Personalidade '{personality}' não encontrada")
    
    def get_system_prompt(self) -> str:
        """Retorna o prompt do sistema baseado na personalidade atual"""
        base_prompt = self.personalities[self.current_personality]["system_prompt"]
        
        # Adiciona informações do sistema
        system_info = f"""
        
Informações do sistema:
- Data/Hora atual: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
- Sistema: Windows
- Você pode executar comandos do sistema e monitorar recursos
- Você tem acesso a funcionalidades de automação e controle

Responda sempre em português brasileiro.
"""
        
        return base_prompt + system_info
    
    async def chat(self, message: str, context: Optional[Dict] = None) -> str:
        """
        Processa uma mensagem de chat
        
        Args:
            message: Mensagem do usuário
            context: Contexto adicional (dados do sistema, etc.)
        
        Returns:
            Resposta da IA
        """
        try:
            self.logger.info(f"💬 Processando mensagem: {message[:50]}...")
            
            # CORREÇÃO: Validar entrada
            if not message or not message.strip():
                return "Por favor, digite uma mensagem válida."
            
            # CORREÇÃO: Prioridade melhorada e fallback garantido
            response = None
            
            # 1. Tentar Ollama Local primeiro
            if self.use_local_ai and self.ollama.check_connection():
                self.logger.info("🧠 Usando Ollama Local")
                try:
                    response = await self._call_ollama_local(message, context)
                except Exception as e:
                    self.logger.error(f"Falha no Ollama: {e}")
                    response = None
            
            # 2. Fallback para OpenAI se disponível
            if not response and self.config.api_key:
                self.logger.info("🌐 Fallback para OpenAI API")
                try:
                    response = await self._call_openai_api_with_context(message, context)
                except Exception as e:
                    self.logger.error(f"Falha na OpenAI: {e}")
                    response = None
            
            # 3. Fallback local se tudo falhar
            if not response:
                self.logger.warning("⚠️ Usando resposta local (fallback)")
                response = self._local_response(message, context)
            
            # CORREÇÃO: Validar resposta final
            if not response or not response.strip():
                response = "Desculpe, não consegui processar sua mensagem no momento. Tente novamente."
            
            # Salva no histórico
            self.conversation_history.append({"role": "user", "content": message})
            self.conversation_history.append({"role": "assistant", "content": response})
            
            # Limita o histórico a 20 mensagens para melhor performance
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            self.logger.info("Resposta gerada com sucesso")
            return response
            
        except Exception as e:
            self.logger.error(f"❌ Erro crítico no chat: {e}")
            return "Desculpe, ocorreu um erro crítico. O sistema está se recuperando. Tente novamente em alguns segundos."
    
    async def _call_ollama_local(self, message: str, context: Optional[Dict] = None) -> str:
        """Chama Ollama Local AI de forma assíncrona"""
        try:
            # Usar modelo específico da personalidade
            current_model = self.personalities[self.current_personality].get("ollama_model", self.DEFAULT_OLLAMA_MODEL)
            self.ollama.set_model(current_model)
            
            # Construir prompt com contexto
            system_prompt = self.get_system_prompt()
            
            if context:
                context_str = f"\n\nContexto do sistema: {json.dumps(context, ensure_ascii=False, indent=2)}"
                system_prompt += context_str
            
            # Incluir histórico recente no prompt
            conversation_context = ""
            if self.conversation_history:
                recent_history = self.conversation_history[-4:]  # CORREÇÃO: Reduzido para 4 mensagens
                for msg in recent_history:
                    role = "Usuário" if msg["role"] == "user" else "Jarvis"
                    conversation_context += f"\n{role}: {msg['content'][:100]}"  # Limite de 100 chars
            
            # Prompt final mais compacto
            full_prompt = f"{system_prompt}\n\nHistórico:{conversation_context}\n\nUsuário: {message}\nJarvis:"
            
            # CORREÇÃO: Executar em thread para não bloquear
            import concurrent.futures
            
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                response = await loop.run_in_executor(
                    executor, 
                    self.ollama.chat,
                    full_prompt
                )
            
            # Limpar possíveis artefatos do prompt
            if response.startswith("Jarvis:"):
                response = response[7:].strip()
            
            return response
            
        except Exception as e:
            self.logger.error(f"Erro no Ollama: {e}")
            return self._fallback_response()
    
    async def _call_openai_api_with_context(self, message: str, context: Optional[Dict] = None) -> str:
        """Chama a API da OpenAI com contexto"""
        try:
            # Constrói o histórico da conversa
            messages = [
                {"role": "system", "content": self.get_system_prompt()}
            ]
            
            # Adiciona contexto se fornecido
            if context:
                context_str = f"Contexto do sistema: {json.dumps(context, ensure_ascii=False, indent=2)}"
                messages.append({"role": "system", "content": context_str})
            
            # Adiciona histórico recente
            messages.extend(self.conversation_history[-10:])  # Últimas 10 mensagens
            
            # Adiciona mensagem atual
            messages.append({"role": "user", "content": message})
            
            response = await openai.ChatCompletion.acreate(
                model=self.config.ai.model_name,
                messages=messages,
                max_tokens=self.config.ai.max_tokens,
                temperature=self.config.ai.temperature,
                stream=False
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.error(f"Erro na API OpenAI: {e}")
            return self._fallback_response()
    
    def _fallback_response(self) -> str:
        """Resposta de fallback quando a API falha"""
        responses = [
            "Estou com dificuldades para processar sua solicitação no momento. Pode tentar novamente?",
            "Desculpe, não consigo acessar minha IA principal agora. Posso ajudar com comandos básicos do sistema.",
            "Parece que há um problema temporário com minha conexão. Que tal verificar o status do sistema?",
        ]
        
        import random
        return random.choice(responses)
    
    def analyze_command(self, text: str) -> Dict[str, Any]:
        """
        Analisa um texto para identificar comandos
        
        Args:
            text: Texto a ser analisado
            
        Returns:
            Dicionário com informações do comando
        """
        text_lower = text.lower()
        
        # Comandos de sistema
        if any(word in text_lower for word in ['cpu', 'processador', 'performance']):
            return {
                'type': 'system_info',
                'action': 'cpu_info',
                'confidence': 0.8
            }
        
        if any(word in text_lower for word in ['memoria', 'ram', 'memória']):
            return {
                'type': 'system_info',
                'action': 'memory_info',
                'confidence': 0.8
            }
        
        # Comandos de plugins
        if any(word in text_lower for word in ['anotar', 'nota', 'anotação']):
            return {
                'type': 'plugin',
                'action': 'add_note',
                'plugin': 'notes',
                'confidence': 0.9
            }
        
        if any(word in text_lower for word in ['lembrar', 'lembrete', 'alarme']):
            return {
                'type': 'plugin',
                'action': 'add_reminder',
                'plugin': 'reminders',
                'confidence': 0.9
            }
        
        if any(word in text_lower for word in ['tarefa', 'task', 'fazer']):
            return {
                'type': 'plugin',
                'action': 'add_task',
                'plugin': 'tasks',
                'confidence': 0.8
            }
        
        if any(word in text_lower for word in ['disco', 'armazenamento', 'hd', 'ssd']):
            return {
                'type': 'system_info',
                'action': 'disk_info',
                'confidence': 0.8
            }
        
        if any(word in text_lower for word in ['bateria', 'energia']):
            return {
                'type': 'system_info',
                'action': 'battery_info',
                'confidence': 0.8
            }
        
        if any(word in text_lower for word in ['temperatura', 'temp']):
            return {
                'type': 'system_info',
                'action': 'temperature_info',
                'confidence': 0.8
            }
        
        # Comandos de aplicação
        if any(word in text_lower for word in ['abrir', 'executar', 'rodar']):
            return {
                'type': 'app_control',
                'action': 'open_app',
                'confidence': 0.7
            }
        
        # Comando de chat geral
        return {
            'type': 'chat',
            'action': 'general_chat',
            'confidence': 0.5
        }
    
    def clear_history(self):
        """Limpa o histórico da conversa"""
        self.conversation_history = []
        self.logger.info("Histórico de conversa limpo")
    
    def get_conversation_summary(self) -> Dict:
        """Retorna um resumo da conversa"""
        return {
            'total_messages': len(self.conversation_history),
            'current_personality': self.personalities[self.current_personality]['name'],
            'last_message_time': datetime.now().isoformat() if self.conversation_history else None
        }
    
    def _local_response(self, message: str, context: Dict = None) -> str:
        """Sistema de resposta local quando não há API key"""
        return self._get_system_response(message, context) or self._get_greeting_response() or self._get_default_response()
    
    def _get_system_response(self, message: str, context: Dict = None) -> Optional[str]:
        """Respostas relacionadas ao sistema"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['cpu', 'processador']):
            if context and 'cpu_percent' in context:
                cpu_val = context['cpu_percent']
                status = "alto" if cpu_val > 80 else "normal"
                return f"CPU: {cpu_val:.1f}% - Status: {status}"
            return "Monitoramento de CPU disponível no dashboard."
        
        if any(word in message_lower for word in ['memoria', 'ram']):
            if context and 'memory_percent' in context:
                mem_val = context['memory_percent']
                status = "alto" if mem_val > 80 else "normal"
                return f"Memória: {mem_val:.1f}% - Status: {status}"
            return "Monitoramento de memória disponível no dashboard."
        
        if any(word in message_lower for word in ['sistema', 'status']):
            if context:
                cpu = context.get('cpu_percent', 0)
                mem = context.get('memory_percent', 0)
                status = "normal" if cpu < 70 and mem < 70 else "alta utilização"
                return f"Sistema: {status}. CPU: {cpu:.1f}%, RAM: {mem:.1f}%"
            return "Sistema operacional. Dashboard ativo."
        
        return None
    
    def _get_greeting_response(self) -> Optional[str]:
        """Respostas de saudação baseadas na personalidade"""
        personality = self.current_personality
        
        greetings = {
            "assistente": "Olá! Como posso ajudá-lo hoje?",
            "tecnico": "Sistema pronto. Aguardando consultas técnicas.",
            "amigavel": "Oi! Tudo bem? Como posso te ajudar?"
        }
        
        return greetings.get(personality)
    
    def _get_default_response(self) -> str:
        """Resposta padrão quando nenhuma IA está disponível"""
        responses = [
            "Sistema em modo local. Funcionalidades limitadas disponíveis.",
            "IA principal indisponível. Usando respostas locais.",
            "Acesse o dashboard para monitoramento em tempo real."
        ]
        
        import random
        return random.choice(responses)
    def _setup_jarvis_model(self):
        """Configura o modelo personalizado do Jarvis"""
        try:
            # Verificar se modelo jarvis-personal já existe
            models = self.ollama.list_models()
            model_names = [m["name"] for m in models]
            
            if "jarvis-personal" not in model_names:
                # Criar modelo personalizado
                modelfile_path = "training_data/Modelfile"
                if self.ollama.create_custom_model("jarvis-personal", modelfile_path):
                    self.logger.info("✅ Modelo Jarvis personalizado criado!")
                else:
                    self.logger.warning("⚠️ Erro criando modelo personalizado. Usando modelo padrão.")
            else:
                self.logger.info("✅ Modelo Jarvis personalizado já existe!")
                
        except Exception as e:
            self.logger.error(f"Erro configurando modelo Jarvis: {e}")
    
    def switch_ai_mode(self, mode: str = "auto"):
        """
        Alterna entre modos de IA
        
        Args:
            mode: 'local', 'api', 'auto'
        """
        if mode == "local" and self.ollama.check_connection():
            self.use_local_ai = True
            self.logger.info("🧠 Modo: IA Local (Ollama)")
        elif mode == "api" and self.config.api_key:
            self.use_local_ai = False
            self.logger.info("🌐 Modo: API OpenAI")
        elif mode == "auto":
            # Auto: prefere local se disponível, senão API
            if self.ollama.check_connection():
                self.use_local_ai = True
                self.logger.info("🧠 Modo: Auto -> IA Local")
            elif self.config.api_key:
                self.use_local_ai = False
                self.logger.info("🌐 Modo: Auto -> API OpenAI")
            else:
                self.logger.warning("⚠️ Modo: Fallback local")
    
    def get_ai_status(self) -> Dict:
        """Retorna status das IAs disponíveis"""
        return {
            "ollama_available": self.ollama.check_connection(),
            "openai_available": bool(self.config.api_key),
            "current_mode": "local" if self.use_local_ai else "api",
            "ollama_models": self.ollama.list_models() if self.ollama.check_connection() else [],
            "current_model": self.personalities[self.current_personality].get("ollama_model", "N/A")
        }
