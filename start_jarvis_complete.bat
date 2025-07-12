@echo off
REM JARVIS 3.0 - Script de Inicialização Rápida
echo 🤖 JARVIS 3.0 - Assistente Virtual Inteligente
echo =====================================

echo.
echo 🔍 Verificando containers Docker...
docker ps | findstr ollama
if %errorlevel% neq 0 (
    echo ⚠️ Container Ollama não está rodando. Iniciando...
    docker-compose up -d ollama
    timeout /t 5 /nobreak > nul
)

echo.
echo 🧠 Verificando disponibilidade do Ollama...
curl -s http://localhost:11434/api/tags > nul
if %errorlevel% neq 0 (
    echo ⚠️ Ollama ainda não está pronto. Aguardando...
    timeout /t 10 /nobreak > nul
)

echo.
echo 🚀 Iniciando JARVIS 3.0...
python main.py --debug

pause
