@echo off
REM ==========================================
REM 🚀 JARVIS 3.0 - Script de Setup para Windows
REM ==========================================

echo 🤖 Bem-vindo ao setup do Jarvis 3.0!
echo ====================================

REM Verifica se Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado. Instale Python 3.8+ antes de continuar.
    pause
    exit /b 1
)

echo ✅ Python encontrado

REM Verifica se pip está instalado
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip não encontrado. Instale pip antes de continuar.
    pause
    exit /b 1
)

echo ✅ pip encontrado

REM Menu principal
:menu
echo.
echo Escolha o tipo de instalação:
echo 1^) Instalação Completa (Recomendado^)
echo 2^) Instalação Básica (Sem modelos^)
echo 3^) Instalação para Desenvolvimento
echo 4^) Verificar Instalação Existente
echo 5^) Sair

set /p choice="Digite sua escolha (1-5): "

if "%choice%"=="1" goto full_installation
if "%choice%"=="2" goto basic_installation
if "%choice%"=="3" goto dev_installation
if "%choice%"=="4" goto check_installation
if "%choice%"=="5" goto end
echo Opção inválida
goto menu

:full_installation
echo 🚀 Iniciando instalação completa...
call :create_venv
call :activate_venv
call :install_dependencies
call :setup_env
call :create_directories
call :download_models
call :test_installation
echo 🎉 Instalação completa concluída!
goto next_steps

:basic_installation
echo 🚀 Iniciando instalação básica...
call :create_venv
call :activate_venv
call :install_dependencies
call :setup_env
call :create_directories
call :test_installation
echo 🎉 Instalação básica concluída!
goto next_steps

:dev_installation
echo 🚀 Iniciando instalação para desenvolvimento...
call :create_venv
call :activate_venv
call :install_dependencies
pip install pytest pytest-cov black flake8 mypy
call :setup_env
call :create_directories
call :test_installation
echo 🎉 Instalação para desenvolvimento concluída!
goto next_steps

:check_installation
echo 🔍 Verificando instalação existente...
call :test_installation
goto menu

:create_venv
echo 📦 Criando ambiente virtual...
if not exist "venv" (
    python -m venv venv
    echo ✅ Ambiente virtual criado
) else (
    echo ⚠️ Ambiente virtual já existe
)
exit /b

:activate_venv
echo 🔧 Ativando ambiente virtual...
call venv\Scripts\activate.bat
echo ✅ Ambiente virtual ativado
exit /b

:install_dependencies
echo 📚 Instalando dependências...
pip install --upgrade pip
pip install -r requirements.txt

if exist "advanced_plugins\requirements.txt" (
    pip install -r advanced_plugins\requirements.txt
)

if exist "plugins\requirements.txt" (
    pip install -r plugins\requirements.txt
)

echo ✅ Dependências instaladas
exit /b

:setup_env
echo ⚙️ Configurando arquivo de ambiente...
if not exist ".env" (
    copy .env.example .env
    echo ✅ Arquivo .env criado a partir do .env.example
    echo ⚠️ IMPORTANTE: Edite o arquivo .env com suas configurações específicas
) else (
    echo ⚠️ Arquivo .env já existe
)
exit /b

:create_directories
echo 📁 Criando diretórios necessários...
if not exist "logs" mkdir logs
if not exist "backups" mkdir backups
if not exist "models" mkdir models
if not exist "audio_cache" mkdir audio_cache
if not exist "temp" mkdir temp
if not exist "data" mkdir data
echo ✅ Diretórios criados
exit /b

:download_models
set /p download_choice="Deseja baixar modelos de IA pré-treinados? (y/n): "
if /i "%download_choice%"=="y" (
    echo 📥 Baixando modelos...
    python download_gpt2.py
    echo ✅ Modelos baixados
) else (
    echo ⏭️ Pulando download de modelos
)
exit /b

:test_installation
echo 🧪 Testando instalação...
python -c "import sys; sys.path.append('.'); from jarvis_entrypoint import Jarvis; print('✅ Instalação OK')"
if %errorlevel% neq 0 (
    echo ❌ Erro na instalação
    pause
    exit /b 1
)
echo ✅ Instalação testada com sucesso
exit /b

:next_steps
echo.
echo 🚀 PRÓXIMOS PASSOS:
echo 1. Edite o arquivo .env com suas configurações
echo 2. Execute: python main.py
echo 3. Ou execute: python -m flask run para interface web
echo 4. Acesse http://localhost:5000 no navegador
echo.
echo 📚 DOCUMENTAÇÃO:
echo - README.md - Documentação completa
echo - CONTRIBUTING.md - Como contribuir
echo.
echo 🆘 SUPORTE:
echo - GitHub Issues para reportar bugs
pause
goto end

:end
echo Até logo! 👋
pause
