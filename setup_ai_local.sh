#!/bin/bash

echo "🚀 Configurando JARVIS 3.0 com IA Local Ollama"
echo "=============================================="

# Parar containers existentes
echo "📦 Parando containers existentes..."
docker stop Ollama_IA_LOCAL Jarvis_WebUI Jarvis_Training 2>/dev/null || true

# Iniciar nova stack completa
echo "🏗️ Iniciando stack completa..."
docker-compose up -d

# Aguardar Ollama ficar pronto
echo "⏳ Aguardando Ollama inicializar..."
sleep 10

# Verificar se modelos estão disponíveis
echo "🧠 Verificando modelos..."
docker exec Ollama_IA_LOCAL ollama list

# Criar modelo personalizado Jarvis
echo "🎯 Criando modelo personalizado do Jarvis..."
docker exec Ollama_IA_LOCAL ollama create jarvis-personal -f /training_data/Modelfile

# Baixar modelos adicionais se necessário
echo "📥 Verificando modelos disponíveis..."
models=$(docker exec Ollama_IA_LOCAL ollama list | wc -l)
if [ $models -lt 3 ]; then
    echo "📥 Baixando modelo adicional..."
    docker exec Ollama_IA_LOCAL ollama pull llama3.2:3b
fi

echo ""
echo "✅ CONFIGURAÇÃO CONCLUÍDA!"
echo "========================="
echo ""
echo "🌐 Acessos disponíveis:"
echo "   • WebUI (ChatGPT-like): http://localhost:3000"
echo "   • Jupyter (Treinamento): http://localhost:8888 (token: jarvis2025)"
echo "   • Ollama API: http://localhost:11434"
echo ""
echo "🤖 Modelos disponíveis:"
docker exec Ollama_IA_LOCAL ollama list
echo ""
echo "🔧 Comandos úteis:"
echo "   • Ver logs: docker-compose logs -f"
echo "   • Parar tudo: docker-compose down"
echo "   • Chat direto: docker exec -it Ollama_IA_LOCAL ollama run jarvis-personal"
echo ""
echo "🎉 Seu Jarvis está pronto para usar!"
