# 🤖 LocalJarvis 3.0 - Assistente Virtual Inteligente

> *"Às vezes você precisa correr antes de poder andar"* - Tony Stark

Um assistente virtual local completo, inspirado no JARVIS do Homem de Ferro, que processa comandos de voz e texto, executa ações no sistema e mantém histórico conversacional. **100% offline, seguro e personalizável**.

## 🎯 **Características Principais**

### 🧠 **Inteligência Artificial**
- ✅ **Modelos de linguagem locais** (LLaMA, GPT-2, Transformers)
- ✅ **Fine-tuning automático** de modelos
- ✅ **Reconhecimento de intenções** avançado
- ✅ **Aprendizado contínuo** baseado em conversas
- ✅ **Múltiplas personalidades** (Formal, Descontraído, Técnico)

### 🎤 **Processamento de Áudio**
- ✅ **Speech-to-Text** com Whisper (offline)
- ✅ **Text-to-Speech** com vozes naturais
- ✅ **Detecção de emoções** por voz
- ✅ **Comando por voz** em tempo real
- ✅ **Suporte multi-idiomas**

### 👁️ **Visão Computacional**
- ✅ **Detecção de objetos** com YOLO/OpenCV
- ✅ **Reconhecimento facial** em tempo real
- ✅ **Análise de imagens** e classificação
- ✅ **Processamento de vídeo** ao vivo
- ✅ **Integração com câmera** do sistema

### 🔒 **Segurança Avançada**
- ✅ **Monitoramento de rede** em tempo real
- ✅ **Detecção de ameaças** e malware
- ✅ **Análise de vulnerabilidades**
- ✅ **Autenticação JWT** e sessões
- ✅ **Rate limiting** e proteção DDoS

### 🎮 **Plugins Especializados**
- ✅ **Assistente Pessoal** - Lembretes, notas, tarefas
- ✅ **Automação** - Scripts e tarefas agendadas  
- ✅ **Controle de Mídia** - Spotify, YouTube, sistema
- ✅ **Clima e Notícias** - APIs integradas
- ✅ **Jogos** - Tic-tac-toe, puzzles, minimax AI
- ✅ **Educação** - Tutoriais, explicações, quizzes

### 🌐 **Interface Moderna**
- ✅ **WebApp responsiva** com Material Design
- ✅ **CLI interativa** para power users
- ✅ **Dashboard de monitoramento**
- ✅ **API RESTful** completa
- ✅ **WebRTC** para áudio em tempo real

## 🚀 **Instalação Rápida**

### **Opção 1: Script Automático (Recomendado)**

**Windows:**
```powershell
git clone <URL_DO_REPOSITORIO>
cd LocalJarvis
.\scripts\setup.bat
```

**Linux/macOS:**
```bash
git clone <URL_DO_REPOSITORIO>
cd LocalJarvis
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### **Opção 2: Instalação Manual**

1. **Pré-requisitos:**
   ```bash
   # Python 3.8+ obrigatório
   python --version
   
   # Git
   git --version
   
   # (Opcional) CUDA para GPU
   nvidia-smi
   ```

2. **Clone e configure:**
   ```bash
   git clone <URL_DO_REPOSITORIO>
   cd LocalJarvis
   
   # Cria ambiente virtual
   python -m venv venv
   
   # Ativa ambiente (Windows)
   venv\Scripts\activate
   
   # Ativa ambiente (Linux/macOS)
   source venv/bin/activate
   
   # Instala dependências
   pip install -r requirements.txt
   pip install -r advanced_plugins/requirements.txt
   ```

3. **Configuração:**
   ```bash
   # Copia arquivo de configuração
   cp .env.example .env
   
   # Edite o arquivo .env com suas configurações
   nano .env  # ou seu editor preferido
   ```

4. **Primeira execução:**
   ```bash
   python main.py
   ```

## ⚙️ **Configuração Detalhada**

### **Arquivo .env**

```bash
# === CONFIGURAÇÕES BÁSICAS ===
JARVIS_NAME=Jarvis
JARVIS_PERSONALITY=Formal  # Formal, Descontraído, Técnico
JARVIS_MODE=Trabalho       # Trabalho, Lazer, Assistente de Voz
LOG_LEVEL=INFO

# === APIS EXTERNAS (Opcional) ===
OPENAI_API_KEY=your_key_here          # Para recursos avançados
GOOGLE_API_KEY=your_key_here          # Para pesquisas
WEATHER_API_KEY=your_key_here         # OpenWeatherMap
NEWS_API_KEY=your_key_here            # NewsAPI

# === SEGURANÇA ===
SECRET_KEY=sua_chave_secreta_aqui
JWT_SECRET_KEY=sua_chave_jwt_aqui
MAX_LOGIN_ATTEMPTS=5
RATE_LIMIT_PER_MINUTE=60

# === PERFORMANCE ===
USE_GPU=false                         # true para CUDA
MAX_CONCURRENT_REQUESTS=10
MODEL_CACHE_SIZE=3
```

### **Configuração de GPU (Opcional)**

Para melhor performance com modelos de IA:

```bash
# 1. Instale CUDA Toolkit (NVIDIA)
# https://developer.nvidia.com/cuda-toolkit

# 2. Instale PyTorch com CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 3. Configure no .env
USE_GPU=true
CUDA_DEVICE=0
GPU_MEMORY_FRACTION=0.8
```

## 🎯 **Como Usar**

### **1. Interface Web (Recomendado)**
```bash
python main.py
# Escolha opção 2 (Web)
# Acesse: http://localhost:5000
```

**Recursos da Interface Web:**
- 🎤 **Comando por voz** - Clique no microfone
- 💬 **Chat inteligente** - Digite comandos ou perguntas
- 🔧 **Configurações** - Altere personalidade e plugins
- 📊 **Dashboard** - Monitore sistema e logs
- 🎮 **Plugins** - Acesse funcionalidades específicas

### **2. Interface CLI (Power Users)**
```bash
python main.py
# Escolha opção 1 (CLI)
```

**Comandos CLI Essenciais:**
```bash
# Comandos básicos
"Olá Jarvis"
"Que horas são?"
"Abrir notepad"
"Pesquisar Python tutorial"

# Lembretes e tarefas
"Criar lembrete comprar leite"
"Listar lembretes"
"Adicionar tarefa estudar IA"

# Visão computacional
"Abrir câmera"
"Detectar objetos"
"Reconhecer faces"

# Segurança
"Monitorar rede"
"Verificar vírus"
"Status de segurança"

# Sistema
"Status do sistema"
"Limpar cache"
"Backup memória"
```

### **3. API RESTful**

```python
import requests

# Autenticação
auth_response = requests.post('http://localhost:5000/api/auth/login', json={
    'username': 'admin',
    'password': 'jarvis123'
})
token = auth_response.json()['session_token']

# Enviar comando de texto
response = requests.post('http://localhost:5000/api/text', 
    json={'text': 'Olá Jarvis'},
    headers={'X-Session-Token': token}
)

# Enviar áudio
with open('audio.wav', 'rb') as f:
    response = requests.post('http://localhost:5000/api/audio',
        files={'file': f},
        headers={'X-Session-Token': token}
    )
```

## 🔌 **Plugins Disponíveis**

### **🤖 Assistente Pessoal**
```bash
# Lembretes
"Criar lembrete reunião às 14h"
"Listar lembretes"
"Remover lembrete #1"

# Notas
"Anotar comprar pão"
"Listar notas"
"Buscar nota pão"

# Tarefas
"Criar tarefa estudar Python"
"Listar tarefas"
"Concluir tarefa #1"

# Cálculos
"Quanto é 25 * 4?"
"Calcular 100 dividido por 5"
```

### **👁️ Visão Computacional**
```bash
# Câmera
"Abrir câmera"
"Tirar foto"

# Detecção
"Detectar objetos na câmera"
"Reconhecer faces"
"Analisar imagem"

# Classificação
"Classificar esta imagem"
"Processar vídeo"
```

### **🔒 Segurança**
```bash
# Monitoramento
"Monitorar rede"
"Verificar processos"
"Status do sistema"

# Verificações
"Verificar vírus"
"Escanear portas"
"Análise de segurança"

# Relatórios
"Relatório de segurança"
"Gerar análise"
```

### **🎮 Automação**
```bash
# Sistema
"Limpar cache"
"Backup dados"
"Reiniciar serviços"

# Agendamento
"Agendar backup diário"
"Executar script"
"Automatizar tarefa"
```

## 🛠️ **Desenvolvimento**

### **Estrutura do Projeto**
```
LocalJarvis/
├── 🧠 core/                 # Núcleo do sistema
│   ├── input_processors.py  # Processadores especializados
│   ├── personality.py       # Sistema de personalidades
│   └── plugin_manager.py    # Gerenciador de plugins
├── 🎤 audio_processing/     # Processamento de áudio
├── 👁️ vision/               # Visão computacional  
├── 🔒 security/             # Módulos de segurança
├── 🔌 advanced_plugins/     # Plugins avançados
├── 🌐 frontend/             # Interface web
├── 📊 utils/                # Utilitários
├── 🧪 tests/                # Testes automatizados
└── 📝 docs/                 # Documentação
```

### **Criando um Plugin Personalizado**

```python
# meu_plugin.py
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class MeuPlugin:
    def __init__(self, config: dict = None):
        self.config = config or {}
        logger.info("MeuPlugin inicializado")
    
    def process(self, text: str) -> Optional[str]:
        """Processa comandos do plugin."""
        if 'meu comando' in text.lower():
            return self._handle_my_command(text)
        return None
    
    def _handle_my_command(self, text: str) -> str:
        """Lida com comando específico."""
        return "🎉 Comando executado com sucesso!"
    
    def on_event(self, event: dict):
        """Recebe eventos do sistema."""
        logger.info(f"Evento recebido: {event}")
```

**Registrando o Plugin:**
```python
# Em plugins/load_plugins.py
from advanced_plugins.meu_plugin import MeuPlugin

def load_plugins(config):
    plugins = {}
    
    if config.get('meu_plugin', {}).get('enabled', False):
        plugins['meu_plugin'] = MeuPlugin(config.get('meu_plugin', {}))
    
    return plugins
```

### **Executando Testes**
```bash
# Instala dependências de desenvolvimento
pip install pytest pytest-cov black flake8 mypy

# Executa todos os testes
pytest tests/

# Com cobertura
pytest --cov=. tests/

# Testes específicos
pytest tests/test_plugins.py -v

# Formatação de código
black . --line-length=100

# Linting
flake8 . --max-line-length=100
```

## 🐳 **Deploy com Docker**

### **Desenvolvimento Local**
```bash
# Build e execução
docker-compose up --build

# Apenas build
docker-compose build

# Em background
docker-compose up -d

# Logs
docker-compose logs -f core
```

### **Produção**
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  core:
    build: .
    environment:
      - FLASK_ENV=production
      - LOG_LEVEL=WARNING
      - USE_GPU=true
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
```

## 📊 **Monitoramento e Logs**

### **Logs Estruturados**
```python
from utils.structured_logger import jarvis_logger

# Logging básico
jarvis_logger.info("Sistema iniciado")
jarvis_logger.error("Erro crítico", module="core", details="...")

# Logging especializado
jarvis_logger.log_user_interaction("Olá", "Oi! Como posso ajudar?", 0.5)
jarvis_logger.log_plugin_activity("vision_plugin", "detect_faces", True)
jarvis_logger.log_security_event("Tentativa de acesso negada", "WARNING")
```

### **Métricas de Performance**
```python
from utils.structured_logger import log_performance_metric

log_performance_metric("response_time", 150.5, "ms")
log_performance_metric("memory_usage", 85.2, "%")
```

### **Dashboard de Monitoramento**
Acesse: `http://localhost:5000/dashboard`

- 📊 **Métricas em tempo real**
- 📈 **Gráficos de performance**
- 🚨 **Alertas de segurança**
- 📝 **Logs filtráveis**
- 🔄 **Status dos serviços**

## 🔧 **Solução de Problemas**

### **Problemas Comuns**

**1. Erro de importação de módulos:**
```bash
# Solução: Ativar ambiente virtual
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

**2. Câmera não funciona:**
```bash
# Verificar dispositivos disponíveis
python -c "import cv2; print(cv2.VideoCapture(0).isOpened())"

# Instalar drivers/libs adicionais no Linux
sudo apt-get install libopencv-dev python3-opencv
```

**3. Modelo de IA lento:**
```bash
# Verificar se está usando GPU
python -c "import torch; print(torch.cuda.is_available())"

# Reduzir tamanho do modelo no config
MAX_TOKENS=256
MODEL_CACHE_SIZE=1
```

**4. Erro de permissões:**
```bash
# Linux: Adicionar usuário ao grupo audio/video
sudo usermod -a -G audio,video $USER

# Windows: Executar como administrador
```

### **Debug Mode**
```bash
# Ativa modo debug
export FLASK_DEBUG=true
export LOG_LEVEL=DEBUG

python main.py
```

### **Logs Detalhados**
```bash
# Visualizar logs em tempo real
tail -f logs/jarvis.log | jq '.'

# Filtrar erros
grep "ERROR" logs/jarvis.log

# Analisar performance
grep "performance_metric" logs/jarvis.log | jq '.value'
```

## 🤝 **Contribuindo**

### **Como Contribuir**
1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### **Diretrizes**
- ✅ Siga o padrão de código (Black, Flake8)
- ✅ Adicione testes para novas funcionalidades
- ✅ Documente APIs e funcionalidades
- ✅ Use commits semânticos
- ✅ Mantenha compatibilidade com versões anteriores

### **Roadmap**
- 🔄 **v3.1** - Integração com IoT (Arduino, Raspberry Pi)
- 🔄 **v3.2** - Mobile app (Flutter)  
- 🔄 **v3.3** - Integração com assistentes (Alexa, Google)
- 🔄 **v3.4** - Blockchain para segurança
- 🔄 **v4.0** - AGI features e reasoning avançado

## 📄 **Licença**

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙏 **Agradecimentos**

- **OpenAI** - Whisper e conceitos de IA
- **Hugging Face** - Transformers e modelos
- **OpenCV** - Visão computacional
- **Flask** - Framework web
- **Comunidade Python** - Bibliotecas incríveis

## 📞 **Suporte**

- 🐛 **Bugs**: [GitHub Issues](https://github.com/seu-usuario/jarvis/issues)
- 💬 **Discussões**: [GitHub Discussions](https://github.com/seu-usuario/jarvis/discussions)
- 📧 **Email**: jarvis-support@exemplo.com
- 💭 **Discord**: [Servidor da Comunidade](#)

---

## 🎉 **Vamos Construir o Futuro Juntos!**

> *"Eu sou o JARVIS, e estou aqui para ajudá-lo a alcançar todo o seu potencial."*

**LocalJarvis 3.0** não é apenas um assistente virtual - é uma plataforma completa para automação, IA e produtividade. Junte-se à comunidade e ajude a construir o assistente dos sonhos!

### ⭐ **Se este projeto foi útil, deixe uma estrela!** ⭐
- Logging avançado e troubleshooting
- Testes automatizados para todos os módulos
- Documentação detalhada e exemplos de uso

## Exemplo de Configuração de Plugins

```yaml
plugins:
  media_control:
    enabled: true
  weather_plugin:
    enabled: true
    api_key: "SUA_API_KEY"
```

## Exemplo de Uso via CLI

```powershell
# Texto
Invoke-RestMethod -Uri http://localhost:5000/text -Method Post -Body (@{text='abrir notepad'} | ConvertTo-Json) -ContentType 'application/json'

# Áudio
Invoke-RestMethod -Uri http://localhost:5000/audio -Method Post -InFile .\audio.wav -ContentType 'audio/wav'
```

## Testes

Execute os testes com:
```powershell
docker-compose exec core pytest tests/
```

## Healthcheck dos Serviços

Execute para validar endpoints principais:
```powershell
bash ./scripts/healthcheck.sh
```

## Logging

Os logs ficam disponíveis em `/app/logs/jarvis.log` dentro do container core.

## Boas Práticas

- Versione imagens: `docker build -t jarvis-core:$(git rev-parse --short HEAD) -f docker/core/Dockerfile .`
- Use CI/CD para build/teste automático.
- Monitore logs em tempo real: `docker-compose logs -f --tail=100 --no-color | tee combined.log`

## Contribuição

Veja `CONTRIBUTING.md` para diretrizes.

## Licença

MIT
