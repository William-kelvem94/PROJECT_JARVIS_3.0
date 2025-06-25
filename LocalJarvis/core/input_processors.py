"""
Processadores de entrada especializados para o Jarvis.
Separa a lógica de processamento em módulos menores e mais focados.
"""

import logging
import re
import tempfile
from typing import Tuple, Optional, Any

logger = logging.getLogger(__name__)

class TrainingProcessor:
    """Processa comandos de treinamento de modelos."""
    
    FINE_TUNED_MODEL_DIR = './fine_tuned_model'
    
    def __init__(self, training_module):
        self.training = training_module
    
    def is_training_command(self, text: str) -> bool:
        """Verifica se o texto é um comando de treinamento."""
        return text.strip().lower().startswith(('treinar', 'train'))
    
    def process_training_command(self, text: str) -> str:
        """Processa comando de treinamento."""
        try:
            modelo, dataset_content = self._parse_training_command(text)
            if not dataset_content:
                return "Comando de treinamento detectado, mas nenhum dataset fornecido. Use: treinar modelo <nome> com dataset <dados>"
            
            dataset_path = self._create_temp_dataset(dataset_content)
            self.training.fine_tune_model(modelo, dataset_path, self.FINE_TUNED_MODEL_DIR)
            return f"Treinamento concluído! Modelo salvo em {self.FINE_TUNED_MODEL_DIR}"
            
        except Exception as e:
            logger.error(f"Erro no treinamento: {e}")
            return f"Erro no treinamento: {e}"
    
    def _parse_training_command(self, text: str) -> Tuple[str, Optional[str]]:
        """Extrai modelo e dataset do comando."""
        modelo = 'gpt2'  # default
        dataset_content = None
        
        modelo_match = re.search(r'modelo\s+(\w+)', text, re.IGNORECASE)
        if modelo_match:
            modelo = modelo_match.group(1)
            
        dataset_match = re.search(r'dataset\s+(.+)', text, re.IGNORECASE)
        if dataset_match:
            dataset_content = dataset_match.group(1)
            
        return modelo, dataset_content
    
    def _create_temp_dataset(self, content: str) -> str:
        """Cria arquivo temporário com dataset."""
        with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt') as tmp:
            tmp.write(content)
            return tmp.name


class AudioProcessor:
    """Processa entradas de áudio."""
    
    def __init__(self, stt_service, tts_service):
        self.stt = stt_service
        self.tts = tts_service
    
    def transcribe_audio(self, audio_data: Any) -> str:
        """Converte áudio para texto."""
        logger.info("Processando entrada de áudio.")
        return self.stt.transcribe(audio_data)
    
    def synthesize_response(self, text: str) -> Any:
        """Converte texto para áudio."""
        logger.info("Gerando resposta de áudio.")
        return self.tts.synthesize(text)


class PluginProcessor:
    """Processa plugins de forma segura e organizada."""
    
    def __init__(self, plugins: dict):
        self.plugins = plugins
    
    def process_plugins(self, text: str, context: str, personality: str, mode: str) -> str:
        """Processa todos os plugins e retorna resultados combinados."""
        plugin_results = []
        
        for plugin_name, plugin in self.plugins.items():
            try:
                result = self._process_single_plugin(plugin, plugin_name, text, context, personality, mode)
                if result:
                    plugin_results.append(f"[{plugin_name}]: {result}")
                    logger.info(f"Plugin {plugin_name} executado com sucesso.")
            except Exception as e:
                logger.warning(f"Plugin {plugin_name} falhou: {e}")
        
        return "\n".join(plugin_results)
    
    def _process_single_plugin(self, plugin: Any, name: str, text: str, context: str, personality: str, mode: str) -> Optional[str]:
        """Processa um plugin individual."""
        # Tenta método process primeiro
        if hasattr(plugin, 'process'):
            try:
                return plugin.process(text)
            except TypeError:
                # Se process não aceita argumento, tenta handle
                return self._try_handle_method(plugin, text)
        
        # Se não tem process, tenta handle
        elif hasattr(plugin, 'handle'):
            return self._try_handle_method(plugin, text)
        
        # Sistema de eventos
        self._send_event_to_plugin(plugin, text, context, personality, mode)
        return None
    
    def _try_handle_method(self, plugin: Any, text: str) -> Optional[str]:
        """Tenta executar método handle do plugin."""
        if hasattr(plugin, 'handle'):
            return plugin.handle(text)
        return None
    
    def _send_event_to_plugin(self, plugin: Any, text: str, context: str, personality: str, mode: str):
        """Envia evento para plugin se suportar."""
        if hasattr(plugin, 'on_event'):
            try:
                plugin.on_event({
                    'input': text,
                    'context': context,
                    'personality': personality,
                    'mode': mode
                })
            except Exception as e:
                logger.warning(f"Falha ao enviar evento para plugin: {e}")


class ConversationLogger:
    """Gerencia logs de conversação para aprendizado contínuo."""
    
    LOG_FILE = "./memory/conversation_log.txt"
    
    def log_conversation(self, user_input: str, assistant_response: str):
        """Registra conversa para aprendizado contínuo."""
        try:
            with open(self.LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"Usuário: {user_input}\nAssistente: {assistant_response}\n")
        except Exception as e:
            logger.warning(f"Falha ao registrar conversa: {e}")


class ResponseProcessor:
    """Processa e gera respostas finais."""
    
    def __init__(self, llm_service, executor_service, memory_service):
        self.llm = llm_service
        self.executor = executor_service
        self.memory = memory_service
    
    def generate_response(self, text: str) -> Tuple[str, Optional[str]]:
        """Gera resposta usando LLM e detecta ações."""
        context = self.memory.get_context()
        logger.debug(f"Contexto recuperado: {context[:100]}...")
        
        response, action = self.llm.infer(text, context)
        logger.info(f"Resposta gerada: {response[:50]}..., Ação: {action}")
        
        return response, action
    
    def execute_action(self, action: str) -> str:
        """Executa ação detectada."""
        if not action:
            return ""
        
        execution_result = self.executor.execute(action)
        logger.info(f"Ação executada: {execution_result}")
        return f"\nResultado: {execution_result}"
    
    def store_interaction(self, user_input: str, response: str):
        """Armazena interação na memória."""
        self.memory.store_interaction(user_input, response)
        logger.debug("Interação armazenada na memória.")
