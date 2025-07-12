@echo off
echo 🧠 JARVIS 3.0 - Inicialização Rápida
echo ====================================

echo.
echo 📦 Verificando Docker...
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker não está rodando!
    echo 💡 Inicie o Docker Desktop primeiro
    pause
    exit /b 1
)

echo.
echo 🔍 Verificando container Ollama...
docker ps | findstr "Ollama_IA_LOCAL" >nul
if %errorlevel% neq 0 (
    echo ⚠️ Container Ollama não encontrado
    echo 🚀 Iniciando Ollama...
    docker run -d --name Ollama_IA_LOCAL -p 11434:11434 ollama/ollama:latest
    echo ⏳ Aguardando Ollama inicializar...
    timeout /t 10 /nobreak >nul
) else (
    echo ✅ Container Ollama já está rodando
)

echo.
echo 🧠 Verificando modelos...
docker exec Ollama_IA_LOCAL ollama list | findstr "llama3.2:1b" >nul
if %errorlevel% neq 0 (
    echo 📥 Baixando modelo básico...
    docker exec Ollama_IA_LOCAL ollama pull llama3.2:1b
)

echo.
echo 🎯 Iniciando interface JARVIS...
echo 📱 Acesse: http://localhost:5000
echo.
echo 🚀 Pressione Ctrl+C para parar
python start_jarvis.py

pause
