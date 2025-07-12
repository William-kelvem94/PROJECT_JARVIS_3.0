# 🤖 JARVIS 3.0 - Assistente Virtual Inteligente Completo

[![Status](https://img.shields.io/badge/Status-FUNCIONAL-00ff00?style=for-the-badge&logo=checkmarx&logoColor=white)](https://github.com)
[![Interface](https://img.shields.io/badge/Interface-MODERNA-0080ff?style=for-the-badge&logo=react&logoColor=white)](https://github.com)
[![IA](https://img.shields.io/badge/IA-LOCAL%2FREMOTA-ff6600?style=for-the-badge&logo=openai&logoColor=white)](https://github.com)

Sistema de assistente virtual avançado com **monitoramento em tempo real**, **IA local/remota**, **interface web moderna** e funcionalidades completas de automação - **TOTALMENTE INTEGRADO** na pasta principal.

## ✨ Principais Características

### 🧠 **IA Híbrida**
- **IA Local**: Ollama integrado (LLaMA 3.2, modelos personalizados)
- **IA Remota**: OpenAI API com fallback inteligente
- **Personalidades**: 3 modos configuráveis (Assistente, Técnico, Amigável)
- **Contexto Inteligente**: Processamento com dados do sistema em tempo real

### 📊 **Dashboard Avançado**
- **Monitoramento Real-time**: CPU, RAM, Disco, Rede, Temperatura, Bateria
- **Gráficos Interativos**: Chart.js com WebSocket para atualizações instantâneas
- **Interface Responsiva**: Design moderno que adapta a qualquer dispositivo
- **Temas**: Modo claro/escuro dinâmico

### 🐳 **Ambiente Containerizado**
- **Docker Compose**: Ollama, WebUI, Jupyter Notebook
- **Auto-Setup**: Containers iniciados automaticamente
- **Isolamento**: Ambiente reproduzível e portável

## 🚀 **INSTALAÇÃO EM 3 PASSOS**

### 1. **Preparar Ambiente**
```bash
# Instalar dependências
pip install -r requirements.txt
```

### 2. **Iniciar Containers**
```bash
# Docker containers (Ollama, WebUI, Jupyter)
docker-compose up -d
```

### 3. **Executar JARVIS**
```bash
# Modo completo com interface web
python main.py --debug

# Modo CLI para interação direta
python main.py --mode cli

# Usando script Windows
start_jarvis_complete.bat
```

### 🌐 **Acessar Interfaces**
- **🎛️ Dashboard Principal**: http://localhost:5000
- **💬 Chat IA**: http://localhost:5000/chat  
- **🔧 WebUI Ollama**: http://localhost:3000
- **📚 Jupyter Notebook**: http://localhost:8888

## 📁 **Estrutura Organizada**

```
PROJECT_JARVIS_3.0/
├── 🧠 core/                    # Núcleo do sistema
│   ├── app.py                 # Flask app principal
│   ├── ai_engine.py           # Motor de IA híbrida
│   ├── config.py              # Sistema de configuração
│   ├── ollama_integration.py  # Integração Ollama
│   ├── plugins.py             # Sistema de plugins
│   └── system_monitor.py      # Monitoramento de recursos
├── 🌐 web/                     # Interface web completa
│   ├── templates/             # HTML templates modernos
│   │   ├── index.html         # Dashboard principal
│   │   ├── chat.html          # Interface de chat
│   │   └── ai_control.html    # Controles de IA
│   └── static/                # Assets (CSS, JS, imagens)
│       ├── css/               # Estilos modernos
│       ├── js/                # JavaScript interativo
│       └── images/            # Ícones e imagens
├── 🔧 utils/                   # Utilitários
│   └── logger_fixed.py        # Sistema de logging avançado
├── 📊 data/                    # Dados do sistema
├── 📝 logs/                    # Logs organizados por data
├── 🤖 models/                  # Modelos de IA
├── 📚 training_data/           # Dados de treinamento Ollama
├── ⚙️ config/                  # Configurações adicionais
├── 🚀 main.py                  # Ponto de entrada principal
├── 📋 config.json              # Configuração principal
├── 📦 requirements.txt         # Dependências Python
├── 🐳 docker-compose.yml       # Configuração containers
└── 🎯 start_jarvis_complete.bat # Script de inicialização
```

## ⚙️ **Configuração**

### **config.json - Configuração Principal**
```json
{
  "ai": {
    "model_name": "gpt-3.5-turbo",
    "api_key": null,                    // Adicione sua chave OpenAI aqui
    "use_local_model": true,            // Prioriza IA local (Ollama)
    "temperature": 0.7
  },
  "web": {
    "host": "localhost",
    "port": 5000,
    "debug": false
  },
  "system": {
    "monitoring_interval": 1,           // Intervalo de monitoramento (segundos)
    "log_level": "INFO"
  }
}
```

### **Personalizar IA**
- **Assistente**: Profissional e direto
- **Técnico**: Especializado em tecnologia  
- **Amigável**: Casual e descontraído

## 🎯 **Funcionalidades Completas**

### 💬 **Chat Inteligente**
- Conversação natural em português
- Contexto do sistema integrado (CPU, RAM, etc.)
- Comandos de sistema ("Como está a CPU?")
- Múltiplas personalidades

### 📈 **Monitoramento Avançado**
- **Tempo Real**: Atualizações via WebSocket
- **Métricas Completas**: CPU, RAM, Disco, Rede, Temperatura
- **Alertas Visuais**: Indicadores de status coloridos
- **Histórico**: Gráficos de performance temporal

### 🔌 **Sistema de Plugins**
- **Anotações**: Sistema de notes persistente
- **Tarefas**: Gerenciador de TO-DO
- **Lembretes**: Sistema de alarmes
- **Comandos**: Automação de sistema

### 🎨 **Interface Moderna**
- **Design Responsivo**: Funciona em desktop e mobile
- **Temas**: Modo claro/escuro
- **Gráficos Interativos**: Chart.js com animações
- **WebSocket**: Atualizações sem refresh

## 🐳 **Containers Docker**

```yaml
# docker-compose.yml - Serviços incluídos
services:
  ollama:          # IA Local - LLaMA 3.2
  open-webui:      # Interface web para Ollama  
  jupyter:         # Notebooks para desenvolvimento
```

### **Comandos Docker Úteis**
```bash
# Status dos containers
docker ps

# Logs de um container específico
docker logs ollama_container

# Reiniciar containers
docker-compose restart

# Parar tudo
docker-compose down
```

## 🔧 **Scripts de Automação**

### **Windows**
```batch
start_jarvis_complete.bat    # Inicialização completa automática
setup_ai_local.bat          # Setup inicial de ambiente
```

### **Comandos de Linha**
```bash
# Diferentes modos de execução
python main.py               # Modo web padrão
python main.py --debug       # Modo debug com logs detalhados
python main.py --mode cli    # Modo terminal interativo
python main.py --port 5001   # Porta personalizada
python main.py --help        # Ver todas as opções
```

## 📊 **APIs Disponíveis**

### **REST API**
```bash
GET  /api/system/info        # Informações do sistema
POST /api/chat               # Chat com IA
GET  /api/ai/personalities   # Listar personalidades
POST /api/ai/personality     # Alterar personalidade
```

### **WebSocket Events**
```javascript
socket.on('system_update')   // Dados de sistema em tempo real
socket.on('chat_response')   // Respostas de chat
socket.emit('start_monitoring') // Iniciar monitoramento
```

## 🚨 **Solução de Problemas**

### **Problemas Comuns**

1. **Ollama não conecta**
   ```bash
   docker-compose restart ollama
   docker logs ollama_container
   ```

2. **Porta já em uso**
   ```bash
   python main.py --port 5001
   ```

3. **Dependências em falta**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

4. **Interface não carrega**
   - Verificar se o servidor está rodando
   - Limpar cache do navegador
   - Verificar logs em `logs/jarvis_YYYYMMDD.log`

### **Logs Detalhados**
```bash
# Ver logs em tempo real
tail -f logs/jarvis_*.log

# Modo debug completo
python main.py --debug
```

## 🔐 **Segurança**

- **CORS configurável** para acesso externo controlado
- **Chaves secretas** configuráveis no config.json
- **Logs de auditoria** para todas as operações
- **Isolamento de containers** para segurança adicional

## 🎉 **Recursos Extras**

### **Personalização Avançada**
- Temas CSS customizáveis
- Intervalos de monitoramento ajustáveis  
- Logs com níveis configuráveis
- Sistema de plugins extensível

### **Desenvolvimento**
- Jupyter Notebooks incluídos
- Sistema de testes automatizados
- Arquitetura modular para extensões
- Documentação de API completa

---

## 🚀 **COMEÇAR AGORA**

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Iniciar containers
docker-compose up -d

# 3. Executar JARVIS
python main.py --debug

# 4. Acessar: http://localhost:5000
```

---

**🎯 JARVIS 3.0** - Sistema completo, moderno e funcional - **Desenvolvido com ❤️ para automação inteligente**

[![Made with Python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED.svg)](https://www.docker.com/)
[![AI Powered](https://img.shields.io/badge/AI-Powered-ff6b6b.svg)](https://ollama.ai/)