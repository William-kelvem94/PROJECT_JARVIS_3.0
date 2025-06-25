#!/bin/bash

# ==========================================
# 🚀 JARVIS 3.0 - Script de Setup Automático
# ==========================================

set -e  # Para na primeira falha

echo "🤖 Bem-vindo ao setup do Jarvis 3.0!"
echo "===================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para logs coloridos
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verifica se Python está instalado
check_python() {
    log_info "Verificando instalação do Python..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        log_success "Python $PYTHON_VERSION encontrado"
    else
        log_error "Python 3 não encontrado. Instale Python 3.8+ antes de continuar."
        exit 1
    fi
}

# Verifica se pip está instalado
check_pip() {
    log_info "Verificando pip..."
    if command -v pip3 &> /dev/null; then
        log_success "pip encontrado"
    else
        log_error "pip não encontrado. Instale pip antes de continuar."
        exit 1
    fi
}

# Cria ambiente virtual
create_venv() {
    log_info "Criando ambiente virtual..."
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        log_success "Ambiente virtual criado"
    else
        log_warning "Ambiente virtual já existe"
    fi
}

# Ativa ambiente virtual
activate_venv() {
    log_info "Ativando ambiente virtual..."
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    log_success "Ambiente virtual ativado"
}

# Instala dependências
install_dependencies() {
    log_info "Instalando dependências..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Instala dependências dos plugins
    if [ -f "advanced_plugins/requirements.txt" ]; then
        pip install -r advanced_plugins/requirements.txt
    fi
    
    if [ -f "plugins/requirements.txt" ]; then
        pip install -r plugins/requirements.txt
    fi
    
    log_success "Dependências instaladas"
}

# Cria arquivo .env se não existir
setup_env() {
    log_info "Configurando arquivo de ambiente..."
    if [ ! -f ".env" ]; then
        cp .env.example .env
        log_success "Arquivo .env criado a partir do .env.example"
        log_warning "IMPORTANTE: Edite o arquivo .env com suas configurações específicas"
    else
        log_warning "Arquivo .env já existe"
    fi
}

# Cria diretórios necessários
create_directories() {
    log_info "Criando diretórios necessários..."
    mkdir -p logs
    mkdir -p backups
    mkdir -p models
    mkdir -p audio_cache
    mkdir -p temp
    mkdir -p data
    log_success "Diretórios criados"
}

# Download de modelos (opcional)
download_models() {
    log_info "Deseja baixar modelos de IA pré-treinados? (y/n)"
    read -r download_choice
    if [[ $download_choice == "y" || $download_choice == "Y" ]]; then
        log_info "Baixando modelos..."
        python3 download_gpt2.py
        log_success "Modelos baixados"
    else
        log_info "Pulando download de modelos"
    fi
}

# Testa instalação
test_installation() {
    log_info "Testando instalação..."
    python3 -c "
import sys
sys.path.append('.')
try:
    from jarvis_entrypoint import Jarvis
    print('✅ Importação do Jarvis OK')
    
    # Testa imports básicos
    from audio_processing.speech_to_text import SpeechToText
    from audio_processing.text_to_speech import TextToSpeech
    from language_model.local_inference import LocalInference
    print('✅ Módulos básicos OK')
    
    print('🎉 Instalação concluída com sucesso!')
except Exception as e:
    print(f'❌ Erro na instalação: {e}')
    sys.exit(1)
"
}

# Menu principal
main_menu() {
    echo ""
    log_info "Escolha o tipo de instalação:"
    echo "1) Instalação Completa (Recomendado)"
    echo "2) Instalação Básica (Sem modelos)"
    echo "3) Instalação para Desenvolvimento"
    echo "4) Verificar Instalação Existente"
    echo "5) Sair"
    
    read -r choice
    case $choice in
        1) full_installation ;;
        2) basic_installation ;;
        3) dev_installation ;;
        4) check_installation ;;
        5) exit 0 ;;
        *) log_error "Opção inválida" && main_menu ;;
    esac
}

# Instalação completa
full_installation() {
    log_info "Iniciando instalação completa..."
    check_python
    check_pip
    create_venv
    activate_venv
    install_dependencies
    setup_env
    create_directories
    download_models
    test_installation
    log_success "🎉 Instalação completa concluída!"
    show_next_steps
}

# Instalação básica
basic_installation() {
    log_info "Iniciando instalação básica..."
    check_python
    check_pip
    create_venv
    activate_venv
    install_dependencies
    setup_env
    create_directories
    test_installation
    log_success "🎉 Instalação básica concluída!"
    show_next_steps
}

# Instalação para desenvolvimento
dev_installation() {
    log_info "Iniciando instalação para desenvolvimento..."
    check_python
    check_pip
    create_venv
    activate_venv
    install_dependencies
    
    # Instala ferramentas de desenvolvimento
    pip install pytest pytest-cov black flake8 mypy pre-commit
    
    setup_env
    create_directories
    
    # Configura pre-commit hooks
    pre-commit install
    
    test_installation
    log_success "🎉 Instalação para desenvolvimento concluída!"
    show_next_steps
}

# Verifica instalação existente
check_installation() {
    log_info "Verificando instalação existente..."
    test_installation
}

# Mostra próximos passos
show_next_steps() {
    echo ""
    log_info "🚀 PRÓXIMOS PASSOS:"
    echo "1. Edite o arquivo .env com suas configurações"
    echo "2. Execute: python3 main.py"
    echo "3. Ou execute: python3 -m flask run para interface web"
    echo "4. Acesse http://localhost:5000 no navegador"
    echo ""
    log_info "📚 DOCUMENTAÇÃO:"
    echo "- README.md - Documentação completa"
    echo "- CONTRIBUTING.md - Como contribuir"
    echo "- docs/ - Documentação técnica"
    echo ""
    log_info "🆘 SUPORTE:"
    echo "- GitHub Issues para reportar bugs"
    echo "- Discord/Telegram para suporte da comunidade"
}

# Executa menu principal
main_menu
