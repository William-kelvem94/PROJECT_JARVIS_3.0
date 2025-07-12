@echo off
echo 🚀 Configurando JARVIS 3.0 com IA Local Ollama
echo ==============================================

REM Parar containers existentes
echo 📦 Parando containers existentes...
docker stop Ollama_IA_LOCAL Jarvis_WebUI Jarvis_Training 2>nul

REM Iniciar nova stack completa
echo 🏗️ Iniciando stack completa...
docker-compose up -d

REM Aguardar Ollama ficar pronto
echo ⏳ Aguardando Ollama inicializar...
timeout /t 10 /nobreak >nul

REM Verificar se modelos estão disponíveis
echo 🧠 Verificando modelos...
docker exec Ollama_IA_LOCAL ollama list

REM Criar modelo personalizado Jarvis
echo 🎯 Criando modelo personalizado do Jarvis...
docker exec Ollama_IA_LOCAL ollama create jarvis-personal -f /training_data/Modelfile

REM Testar modelo personalizado
echo 🧪 Testando modelo personalizado...
docker exec Ollama_IA_LOCAL ollama run jarvis-personal "Olá, eu sou o Will. Como você está?"

echo.
echo ✅ CONFIGURAÇÃO CONCLUÍDA!
echo =========================
echo.
echo 🌐 Acessos disponíveis:
echo    • WebUI (ChatGPT-like): http://localhost:3000
echo    • Jupyter (Treinamento): http://localhost:8888 (token: jarvis2025)
echo    • Ollama API: http://localhost:11434
echo.
echo 🤖 Para testar seu Jarvis personalizado:
echo    docker exec -it Ollama_IA_LOCAL ollama run jarvis-personal
echo.
echo 🔧 Comandos úteis:
echo    • Ver logs: docker-compose logs -f
echo    • Parar tudo: docker-compose down
echo    • Chat direto: docker exec -it Ollama_IA_LOCAL ollama run jarvis-personal
echo.
echo 🎉 Seu Jarvis está pronto para usar!
pause
