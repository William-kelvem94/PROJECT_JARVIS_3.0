"""
🧠 Ollama Local AI Integration para Jarvis 3.0
Integração com IA local usando Ollama Docker container
"""

import requests
import json
import asyncio
from typing import Dict, List, Optional, Any
import logging

class OllamaLocalAI:
    def __init__(self, base_url: str = "http://localhost:11434"):
        """
        Inicializa conexão com Ollama local
        
        Args:
            base_url: URL do servidor Ollama (padrão: localhost:11434)
        """
        self.base_url = base_url
        self.current_model = "llama3.2:1b"  # Modelo padrão
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
        
    def check_connection(self) -> bool:
        """Verifica se Ollama está respondendo"""
        try:
            self.logger.info("🔍 Verificando conexão com Ollama...")
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                self.logger.info(f"✅ Ollama conectado! {len(models)} modelos disponíveis")
                
                # Verificar se o modelo padrão existe
                available_models = [m["name"] for m in models]
                if self.current_model not in available_models:
                    # Tentar usar o primeiro modelo disponível
                    if available_models:
                        self.current_model = available_models[0]
                        self.logger.info(f"🔄 Modelo padrão alterado para: {self.current_model}")
                
                return True
            else:
                self.logger.error(f"❌ Ollama respondeu com status {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            self.logger.error("⏰ Timeout conectando ao Ollama")
            return False
        except requests.exceptions.ConnectionError:
            self.logger.error("🔌 Erro de conexão com Ollama")
            return False
        except Exception as e:
            self.logger.error(f"❌ Erro conectando Ollama: {e}")
            return False
    
    def list_models(self) -> List[Dict]:
        """Lista modelos disponíveis"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                return response.json().get("models", [])
            return []
        except Exception as e:
            self.logger.error(f"Erro listando modelos: {e}")
            return []
    
    def set_model(self, model_name: str) -> bool:
        """Define modelo ativo"""
        models = self.list_models()
        available_models = [m["name"] for m in models]
        
        # Tentar encontrar modelo exato ou com suffix :latest
        target_model = model_name
        if model_name not in available_models:
            if f"{model_name}:latest" in available_models:
                target_model = f"{model_name}:latest"
            elif model_name.endswith(":latest") and model_name[:-7] in available_models:
                target_model = model_name[:-7]
        
        if target_model in available_models:
            self.current_model = target_model
            self.logger.info(f"Modelo ativo: {target_model}")
            return True
        else:
            self.logger.warning(f"Modelo {model_name} não encontrado. Disponíveis: {available_models}")
            return False
    
    def chat(self, message: str, context: Optional[List] = None) -> str:
        """
        Conversa com IA local
        
        Args:
            message: Mensagem do usuário
            context: Contexto da conversa (opcional)
            
        Returns:
            Resposta da IA
        """
        try:
            # Preparar payload
            payload = {
                "model": self.current_model,
                "prompt": message,
                "stream": False,
                "options": {
                    "temperature": 0.8,
                    "top_p": 0.9,
                    "top_k": 40,
                    "num_ctx": 2048,  # Contexto limitado para evitar timeout
                    "num_predict": 512  # Limita resposta para evitar timeout
                }
            }
            
            # Se há contexto, incluir
            if context:
                payload["context"] = context
            
            # CORREÇÃO: Fazer requisição com timeout mais conservador
            self.logger.info(f"🤖 Enviando mensagem para {self.current_model}: {message[:50]}...")
            
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=30  # CORREÇÃO: Reduzido para 30 segundos
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get("response", "").strip()
                
                # CORREÇÃO: Validar se a resposta não está vazia
                if not ai_response:
                    self.logger.warning("Resposta vazia do Ollama")
                    return "Desculpe, não consegui gerar uma resposta. Pode reformular sua pergunta?"
                
                self.logger.info(f"✅ Resposta gerada com sucesso ({len(ai_response)} caracteres)")
                return ai_response
            else:
                self.logger.error(f"Erro HTTP {response.status_code}: {response.text}")
                return "Desculpe, houve um problema na comunicação com a IA. Tente novamente."
                
        except requests.exceptions.Timeout:
            self.logger.error("Timeout na requisição para Ollama")
            return "A IA está demorando para responder. Tente uma pergunta mais simples."
        except requests.exceptions.ConnectionError:
            self.logger.error("Erro de conexão com Ollama")
            return "Não consegui conectar com a IA local. Verifique se o serviço está rodando."
        except Exception as e:
            self.logger.error(f"Erro inesperado no chat: {e}")
            return "Desculpe, houve um erro interno. Tente novamente."
    
    def chat_stream(self, message: str):
        """Chat com streaming (respostas em tempo real)"""
        try:
            payload = {
                "model": self.current_model,
                "prompt": message,
                "stream": True
            }
            
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                stream=True
            )
            
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        if 'response' in data:
                            yield data['response']
                        if data.get('done', False):
                            break
                    except json.JSONDecodeError:
                        continue
                        
        except Exception as e:
            self.logger.error(f"Erro no streaming: {e}")
            yield "Erro no streaming de resposta."
    
    def create_custom_model(self, model_name: str, modelfile_path: str) -> bool:
        """
        Cria modelo personalizado a partir de Modelfile
        
        Args:
            model_name: Nome do novo modelo
            modelfile_path: Caminho para o Modelfile
            
        Returns:
            True se criado com sucesso
        """
        try:
            with open(modelfile_path, 'r', encoding='utf-8') as f:
                modelfile_content = f.read()
            
            payload = {
                "name": model_name,
                "modelfile": modelfile_content
            }
            
            response = self.session.post(
                f"{self.base_url}/api/create",
                json=payload
            )
            
            return response.status_code == 200
            
        except Exception as e:
            self.logger.error(f"Erro criando modelo: {e}")
            return False
    
    def pull_model(self, model_name: str) -> bool:
        """Baixa um modelo do repositório"""
        try:
            payload = {"name": model_name}
            response = self.session.post(
                f"{self.base_url}/api/pull",
                json=payload
            )
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Erro baixando modelo: {e}")
            return False
    
    def get_model_info(self, model_name: str = None) -> Dict:
        """Informações sobre um modelo"""
        if not model_name:
            model_name = self.current_model
            
        try:
            payload = {"name": model_name}
            response = self.session.post(
                f"{self.base_url}/api/show",
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            self.logger.error(f"Erro obtendo info do modelo: {e}")
            return {}

# Exemplo de uso
if __name__ == "__main__":
    # Inicializar IA local
    ai = OllamaLocalAI()
    
    # Verificar conexão
    if ai.check_connection():
        print("🟢 Ollama conectado!")
        
        # Listar modelos
        models = ai.list_models()
        print(f"📋 Modelos disponíveis: {[m['name'] for m in models]}")
        
        # Chat simples
        response = ai.chat("Olá Jarvis, como você está?")
        print(f"🤖 Jarvis: {response}")
        
        # Chat com streaming
        print("\n🔄 Resposta em tempo real:")
        for chunk in ai.chat_stream("Me conte uma curiosidade sobre IA"):
            print(chunk, end='', flush=True)
        print()
        
    else:
        print("❌ Ollama não conectado. Verifique se o container está rodando.")
