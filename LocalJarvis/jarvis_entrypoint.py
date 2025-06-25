import yaml
import logging
import sys
import json
import queue
import os
from flask import Flask, request, jsonify
from audio_processing.speech_to_text import SpeechToText
from audio_processing.text_to_speech import TextToSpeech
from command_execution.program_executor import ProgramExecutor
from language_model.local_inference import LocalInference
from language_model import training
from memory.memory_manager import MemoryManager
from interface.web_interface import web_bp
from plugins.load_plugins import load_plugins

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class Jarvis:
    """Classe principal do assistente virtual LocalJarvis."""
    
    def __init__(self, config_path="/app/config/system_config.yaml", json_config_path="config/config.json"):
        """Inicializa o Jarvis com configuração do YAML e módulos."""
        # Carrega YAML (legado)
        try:
            with open(config_path, 'r') as file:
                self.config = yaml.safe_load(file)
        except FileNotFoundError:
            logger.error(f"Arquivo de configuração {config_path} não encontrado.")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Erro ao parsear YAML: {e}")
            raise
        # Carrega JSON (novo)
        try:
            with open(json_config_path, 'r') as file:
                self.json_config = json.load(file)
        except Exception as e:
            logger.warning(f"Configuração JSON não carregada: {e}")
            self.json_config = {}
        # Inicialização dos módulos com configuração
        self.stt = SpeechToText(self.config['stt']['docker_url'], timeout=self.config['stt'].get('timeout', 10))
        self.tts = TextToSpeech(self.config['tts']['docker_url'], voice=self.config['tts'].get('voice', 'default'))
        self.executor = ProgramExecutor(self.config['executor']['allowed_commands'])
        self.llm = LocalInference(self.config['llm']['model_path'], max_tokens=self.config['llm'].get('max_tokens', 512))
        self.memory = MemoryManager(self.config['memory']['db_path'])
        # Plugins agora usam config combinada
        plugins_config = self.json_config.get('plugins', self.config.get('plugins', {}))
        from plugins.load_plugins import load_plugins
        self.plugins = load_plugins(plugins_config)
        # Perfis e modos
        self.personality = self.json_config.get('default_personality', 'Formal')
        self.mode = self.json_config.get('default_mode', 'Trabalho')
        logger.info(f"Perfil: {self.personality} | Modo: {self.mode}")
        logger.info(f"Plugins carregados: {list(self.plugins.keys())}")

        self.event_queue = queue.Queue()

    def process_input(self, input_data, input_type='text'):
        """Processa entrada de texto ou áudio e retorna a resposta."""
        try:
            # Inicializa processadores se não existirem
            if not hasattr(self, '_processors_initialized'):
                self._initialize_processors()
            
            # Processa comando de treinamento primeiro
            if input_type == 'text' and self.training_processor.is_training_command(str(input_data)):
                return self.training_processor.process_training_command(str(input_data))
            
            # Converte áudio para texto se necessário
            text = self._convert_input_to_text(input_data, input_type)
            logger.info(f"Processando entrada: {text}")
            
            # Gera resposta principal
            response = self._generate_main_response(text)
            
            # Processa plugins
            plugin_results = self.plugin_processor.process_plugins(
                text, self.memory.get_context(), self.personality, self.mode
            )
            if plugin_results:
                response += "\n" + plugin_results
            
            # Registra conversa para aprendizado
            self.conversation_logger.log_conversation(text, response)
            
            # Retorna resposta no formato apropriado
            return self._format_response(response, input_type)
        
        except Exception as e:
            logger.error(f"Erro ao processar entrada: {e}", exc_info=True)
            raise
    
    def _initialize_processors(self):
        """Inicializa os processadores especializados."""
        from core.input_processors import (
            TrainingProcessor, AudioProcessor, PluginProcessor,
            ConversationLogger, ResponseProcessor
        )
        
        self.training_processor = TrainingProcessor(training)
        self.audio_processor = AudioProcessor(self.stt, self.tts)
        self.plugin_processor = PluginProcessor(self.plugins)
        self.conversation_logger = ConversationLogger()
        self.response_processor = ResponseProcessor(self.llm, self.executor, self.memory)
        self._processors_initialized = True
    
    def _convert_input_to_text(self, input_data, input_type):
        """Converte entrada para texto."""
        if input_type == 'audio':
            return self.audio_processor.transcribe_audio(input_data)
        return str(input_data)
    
    def _generate_main_response(self, text):
        """Gera resposta principal usando LLM."""
        response, action = self.response_processor.generate_response(text)
        
        # Executa ação se detectada
        action_result = self.response_processor.execute_action(action)
        if action_result:
            response += action_result
        
        # Armazena interação
        self.response_processor.store_interaction(text, response)
        
        return response
    
    def _format_response(self, response, input_type):
        """Formata resposta no tipo apropriado."""
        if input_type == 'audio':
            return self.audio_processor.synthesize_response(response)
        return response

    def set_personality(self, personality):
        """Altera a personalidade do assistente."""
        if personality in self.json_config.get('personality_profiles', []):
            self.personality = personality
            logger.info(f"Personalidade alterada para: {personality}")
            return True
        return False

    def set_mode(self, mode):
        """Altera o modo de operação do assistente."""
        if mode in self.json_config.get('operation_modes', []):
            self.mode = mode
            logger.info(f"Modo de operação alterado para: {mode}")
            return True
        return False

    def get_personality(self):
        """Retorna a personalidade atual do assistente."""
        return self.personality

    def get_mode(self):
        """Retorna o modo de operação atual do assistente."""
        return self.mode

    def get_custom_commands(self):
        """Retorna os comandos personalizados configurados."""
        return self.json_config.get('custom_commands', {})

    def publish_event(self, event):
        self.event_queue.put(event)

    def consume_event(self):
        if not self.event_queue.empty():
            return self.event_queue.get()
        return None

# Configuração da aplicação Flask
app = Flask(__name__)
app.register_blueprint(web_bp)
jarvis_instance = None

def initialize_jarvis():
    """Inicializa a instância global do Jarvis."""
    global jarvis_instance
    if jarvis_instance is None:
        jarvis_instance = Jarvis()
    return jarvis_instance

@app.route('/text', methods=['POST'])
def text_input():
    """Endpoint para entrada de texto via API."""
    try:
        data = request.json.get('text', '')
        jarvis = initialize_jarvis()
        response = jarvis.process_input(data, 'text')
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/audio', methods=['POST'])
def audio_input():
    """Endpoint para entrada de áudio via API."""
    try:
        audio = request.data
        jarvis = initialize_jarvis()
        audio_response = jarvis.process_input(audio, 'audio')
        return audio_response, 200, {'Content-Type': 'audio/wav'}
    except Exception as e:
        return str(e), 500

@app.route('/train', methods=['POST'])
def train_model():
    """Endpoint para treinamento (fine-tuning) da IA."""
    try:
        data = request.json
        model_path = data.get('model_path', 'gpt2')
        output_dir = data.get('output_dir', './fine_tuned_model')
        dataset_content = data.get('dataset_content')
        if not dataset_content:
            return jsonify({'error': 'dataset_content é obrigatório'}), 400
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt') as tmp:
            tmp.write(dataset_content)
            dataset_path = tmp.name
        training.fine_tune_model(model_path, dataset_path, output_dir)
        return jsonify({'message': f'Modelo treinado e salvo em {output_dir}'}), 200
    except Exception as e:
        logger.error(f"Erro no treinamento: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/set_personality', methods=['POST'])
def set_personality():
    """Endpoint para alterar a personalidade do assistente."""
    try:
        personality = request.json.get('personality')
        jarvis = initialize_jarvis()
        if jarvis.set_personality(personality):
            return jsonify({'message': f'Personalidade alterada para {personality}'}), 200
        return jsonify({'error': 'Personalidade inválida'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/set_mode', methods=['POST'])
def set_mode():
    """Endpoint para alterar o modo de operação do assistente."""
    try:
        mode = request.json.get('mode')
        jarvis = initialize_jarvis()
        if jarvis.set_mode(mode):
            return jsonify({'message': f'Modo alterado para {mode}'}), 200
        return jsonify({'error': 'Modo inválido'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/custom_commands', methods=['GET'])
def get_custom_commands():
    """Endpoint para consultar comandos personalizados."""
    try:
        jarvis = initialize_jarvis()
        return jsonify(jarvis.get_custom_commands())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/run_tests', methods=['POST'])
def run_tests():
    """Endpoint para rodar testes automatizados e retornar o resultado como texto."""
    import subprocess
    try:
        result = subprocess.run(['pytest', 'tests/', '--maxfail=10', '--disable-warnings', '-q'], capture_output=True, text=True, timeout=60)
        output = result.stdout + '\n' + result.stderr
        return {'output': output}
    except Exception as e:
        return {'output': f'Erro ao rodar testes: {e}'}

@app.route('/train_from_log', methods=['POST'])
def train_from_log():
    """Endpoint para treinar incrementalmente a partir do log de conversas."""
    try:
        from language_model import training
        log_path = "./memory/conversation_log.txt"
        if not os.path.exists(log_path):
            return jsonify({'error': 'Nenhum log de conversa encontrado.'}), 400
        output_dir = './fine_tuned_model'
        training.fine_tune_model('gpt2', log_path, output_dir)
        return jsonify({'message': f'Modelo incremental treinado e salvo em {output_dir}'}), 200
    except Exception as e:
        logger.error(f"Erro no treinamento incremental: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/stt', methods=['POST'])
def stt_endpoint():
    """Endpoint unificado para transcrição de áudio (STT) na mesma porta."""
    try:
        audio = request.data
        jarvis = initialize_jarvis()
        text = jarvis.stt.transcribe(audio)
        return jsonify({'text': text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/tts', methods=['POST'])
def tts_endpoint():
    """Endpoint unificado para síntese de texto em áudio (TTS) na mesma porta."""
    try:
        data = request.json.get('text', '')
        jarvis = initialize_jarvis()
        audio = jarvis.tts.synthesize(data)
        return audio, 200, {'Content-Type': 'audio/wav'}
    except Exception as e:
        return str(e), 500

@app.route('/api/plugins', methods=['GET'])
def get_active_plugins():
    """Retorna plugins ativos para o frontend (dinâmico)."""
    jarvis = initialize_jarvis()
    plugins = []
    for name, plugin in jarvis.plugins.items():
        plugins.append({
            'name': name,
            'icon': getattr(plugin, 'icon_base64', ''),  # Opcional: plugin pode definir
            'status': getattr(plugin, 'get_status', lambda: 'ativo')(),
            'actions': getattr(plugin, 'available_actions', lambda: [])()
        })
    return jsonify(plugins)

if __name__ == "__main__":
    logger.info("Iniciando servidor web na porta 5000...")
    app.run(host='0.0.0.0', port=5000, debug=False)
