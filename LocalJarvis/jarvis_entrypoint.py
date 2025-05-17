import yaml
import logging
import sys
from flask import Flask, request, jsonify
from audio_processing.speech_to_text import SpeechToText
from audio_processing.text_to_speech import TextToSpeech
from command_execution.program_executor import ProgramExecutor
from language_model.local_inference import LocalInference
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
    
    def __init__(self, config_path="/app/config/system_config.yaml"):
        """Inicializa o Jarvis com configuração do YAML e módulos."""
        try:
            with open(config_path, 'r') as file:
                self.config = yaml.safe_load(file)
        except FileNotFoundError:
            logger.error(f"Arquivo de configuração {config_path} não encontrado.")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Erro ao parsear YAML: {e}")
            raise

        # Inicialização dos módulos com configuração
        self.stt = SpeechToText(self.config['stt']['docker_url'], timeout=self.config['stt'].get('timeout', 10))
        self.tts = TextToSpeech(self.config['tts']['docker_url'], voice=self.config['tts'].get('voice', 'default'))
        self.executor = ProgramExecutor(self.config['executor']['allowed_commands'])
        self.llm = LocalInference(self.config['llm']['model_path'], max_tokens=self.config['llm'].get('max_tokens', 512))
        self.memory = MemoryManager(self.config['memory']['db_path'])
        self.plugins = load_plugins(self.config.get('plugins', {}))
        logger.info("Jarvis inicializado com sucesso.")
        logger.info(f"Plugins carregados: {list(self.plugins.keys())}")

    def process_input(self, input_data, input_type='text'):
        """Processa entrada de texto ou áudio e retorna a resposta."""
        try:
            # Converte áudio para texto, se necessário
            if input_type == 'audio':
                logger.info("Processando entrada de áudio.")
                text = self.stt.transcribe(input_data)
            else:
                text = input_data
                logger.info(f"Processando entrada de texto: {text}")

            # Recupera contexto da memória
            context = self.memory.get_context()
            logger.debug(f"Contexto recuperado: {context[:100]}...")

            # Gera resposta e detecta ação com o modelo de linguagem
            response, action = self.llm.infer(text, context)
            logger.info(f"Resposta gerada: {response[:50]}..., Ação: {action}")

            # Executa ação, se houver
            if action:
                execution_result = self.executor.execute(action)
                response += f"\nResultado: {execution_result}"
                logger.info(f"Ação executada: {execution_result}")

            # Armazena interação na memória
            self.memory.store_interaction(text, response)
            logger.debug("Interação armazenada na memória.")

            # Após gerar resposta, verifica se algum plugin pode ser chamado
            for plugin_name, plugin in self.plugins.items():
                if hasattr(plugin, 'process'):
                    plugin_result = plugin.process(text)
                    if plugin_result:
                        response += f"\n[{plugin_name}]: {plugin_result}"
                        logger.info(f"Plugin {plugin_name} executado.")

            # Retorna resposta em texto ou áudio
            if input_type == 'audio':
                audio_response = self.tts.synthesize(response)
                logger.info("Resposta de áudio gerada.")
                return audio_response
            return response
        except Exception as e:
            logger.error(f"Erro ao processar entrada: {e}", exc_info=True)
            raise

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

if __name__ == "__main__":
    logger.info("Iniciando servidor web na porta 5000...")
    app.run(host='0.0.0.0', port=5000, debug=False)
