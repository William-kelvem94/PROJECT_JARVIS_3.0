"""
Configuração do sistema JARVIS 3.0
"""

import os
import json
import yaml
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional

@dataclass
class AIConfig:
    """Configurações de IA"""
    model_name: str = "gpt-3.5-turbo"
    api_key: Optional[str] = None
    max_tokens: int = 2000
    temperature: float = 0.7
    local_model_path: Optional[str] = None
    use_local_model: bool = False

@dataclass
class SystemConfig:
    """Configurações do sistema"""
    monitoring_interval: int = 1  # segundos
    auto_cleanup: bool = True
    max_memory_usage: float = 80.0  # porcentagem
    max_cpu_usage: float = 90.0  # porcentagem
    log_level: str = "INFO"

@dataclass
class WebConfig:
    """Configurações da interface web"""
    host: str = "localhost"
    port: int = 5000
    debug: bool = False
    secret_key: str = "jarvis-secret-key-change-me"
    enable_cors: bool = True

@dataclass
class AudioConfig:
    """Configurações de áudio"""
    input_device: Optional[int] = None
    output_device: Optional[int] = None
    sample_rate: int = 16000
    chunk_size: int = 1024
    tts_voice: str = "pt-br"
    tts_speed: float = 1.0

class Config:
    """Classe principal de configuração do JARVIS"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.config_dir = self.config_file.parent
        
        # Configurações padrão
        self.ai = AIConfig()
        self.system = SystemConfig()
        self.web = WebConfig()
        self.audio = AudioConfig()
        
        # Carrega configurações personalizadas
        self.load_config()
        
        # Setup de variáveis de ambiente
        self.setup_environment()
    
    def load_config(self):
        """Carrega configurações do arquivo"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Atualiza configurações com dados do arquivo
                if 'ai' in data:
                    self.ai = AIConfig(**data['ai'])
                if 'system' in data:
                    self.system = SystemConfig(**data['system'])
                if 'web' in data:
                    self.web = WebConfig(**data['web'])
                if 'audio' in data:
                    self.audio = AudioConfig(**data['audio'])
                    
            except Exception as e:
                print(f"⚠️ Erro ao carregar configuração: {e}")
                print("📄 Usando configurações padrão")
    
    def save_config(self):
        """Salva configurações no arquivo"""
        try:
            # Cria diretório se não existir
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            data = {
                'ai': asdict(self.ai),
                'system': asdict(self.system),
                'web': asdict(self.web),
                'audio': asdict(self.audio)
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"❌ Erro ao salvar configuração: {e}")
    
    def setup_environment(self):
        """Configura variáveis de ambiente"""
        # OpenAI API Key
        if self.ai.api_key:
            os.environ['OPENAI_API_KEY'] = self.ai.api_key
        
        # Log level
        os.environ['LOG_LEVEL'] = self.system.log_level
    
    def get_data_dir(self) -> Path:
        """Retorna o diretório de dados"""
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        return data_dir
    
    def get_logs_dir(self) -> Path:
        """Retorna o diretório de logs"""
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        return logs_dir
    
    def get_models_dir(self) -> Path:
        """Retorna o diretório de modelos"""
        models_dir = Path("models")
        models_dir.mkdir(exist_ok=True)
        return models_dir
