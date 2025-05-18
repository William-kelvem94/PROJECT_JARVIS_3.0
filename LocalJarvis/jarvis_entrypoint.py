import yaml
import logging
import sys
import json
import queue
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
        # Intercepta comando de treinamento antes de qualquer processamento
        if input_type == 'text' and str(input_data).strip().lower().startswith(('treinar', 'train')):
            import re
            modelo = 'gpt2'
            output_dir = './fine_tuned_model'
            dataset_content = None
            m = re.search(r'modelo\s+(\w+)', input_data, re.IGNORECASE)
            if m:
                modelo = m.group(1)
            d = re.search(r'dataset\s+(.+)', input_data, re.IGNORECASE)
            if d:
                dataset_content = d.group(1)
            if not dataset_content:
                return "Comando de treinamento detectado, mas nenhum dataset fornecido. Use: treinar modelo <nome> com dataset <dados>"
            try:
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt') as tmp:
                    tmp.write(dataset_content)
                    dataset_path = tmp.name
                training.fine_tune_model(modelo, dataset_path, output_dir)
                return f"Treinamento concluído! Modelo salvo em {output_dir}"
            except Exception as e:
                logger.error(f"Erro no treinamento: {e}")
                return f"Erro no treinamento: {e}"
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
                # Chama process se existir e aceitar argumento
                if hasattr(plugin, 'process'):
                    try:
                        result = plugin.process(text)
                        if result:
                            response += f"\n[{plugin_name}]: {result}"
                            logger.info(f"Plugin {plugin_name} executado.")
                    except TypeError as e:
                        # Se process não aceita argumento, tenta handle
                        if hasattr(plugin, 'handle'):
                            try:
                                result = plugin.handle(text)
                                if result:
                                    response += f"\n[{plugin_name}]: {result}"
                                    logger.info(f"Plugin {plugin_name} executado via handle.")
                            except Exception as e2:
                                logger.warning(f"Plugin {plugin_name} falhou ao processar via handle: {e2}")
                        else:
                            logger.warning(f"Plugin {plugin_name} não tem método process(text) nem handle(text): {e}")
                    except Exception as e:
                        logger.warning(f"Plugin {plugin_name} falhou ao processar: {e}")
                elif hasattr(plugin, 'handle'):
                    try:
                        result = plugin.handle(text)
                        if result:
                            response += f"\n[{plugin_name}]: {result}"
                            logger.info(f"Plugin {plugin_name} executado via handle.")
                    except Exception as e:
                        logger.warning(f"Plugin {plugin_name} falhou ao processar via handle: {e}")
                # Sistema de eventos: envia evento para plugins que implementam on_event
                if hasattr(plugin, 'on_event'):
                    try:
                        plugin.on_event({
                            'input': text,
                            'context': context,
                            'personality': self.personality,
                            'mode': self.mode
                        })
                    except Exception as e:
                        logger.warning(f"Plugin {plugin_name} falhou ao processar evento: {e}")

            # Retorna resposta em texto ou áudio
            if input_type == 'audio':
                audio_response = self.tts.synthesize(response)
                logger.info("Resposta de áudio gerada.")
                return audio_response
            return response
        except Exception as e:
            logger.error(f"Erro ao processar entrada: {e}", exc_info=True)
            raise

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

if __name__ == "__main__":
    logger.info("Iniciando servidor web na porta 5000...")
    app.run(host='0.0.0.0', port=5000, debug=False)
