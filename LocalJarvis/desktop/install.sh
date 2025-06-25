#!/bin/bash

echo ""
echo "============================================================"
echo "  JARVIS 3.0 - INSTALAÇÃO DA VERSÃO DESKTOP"
echo "============================================================"
echo ""

# Verifica se Node.js está instalado
if ! command -v node &> /dev/null; then
    echo "❌ Node.js não encontrado!"
    echo "📥 Instale o Node.js:"
    echo "   Ubuntu/Debian: sudo apt-get update && sudo apt-get install nodejs npm"
    echo "   CentOS/RHEL: sudo yum install nodejs npm"
    echo "   macOS: brew install node"
    echo "   Ou baixe em: https://nodejs.org/"
    echo ""
    exit 1
fi

echo "✅ Node.js encontrado!"
node --version

# Verifica se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado!"
    echo "📥 Instale o Python3:"
    echo "   Ubuntu/Debian: sudo apt-get install python3 python3-pip"
    echo "   CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "   macOS: brew install python3"
    echo ""
    exit 1
fi

echo "✅ Python3 encontrado!"
python3 --version

echo ""
echo "📦 Instalando dependências do Electron..."
cd "$(dirname "$0")"
npm install

if [ $? -ne 0 ]; then
    echo "❌ Erro ao instalar dependências!"
    exit 1
fi

echo ""
echo "✅ Instalação concluída!"
echo ""
echo "🚀 Para executar o JARVIS Desktop:"
echo "   npm start"
echo ""
echo "📦 Para criar um instalador:"
echo "   npm run dist"
echo ""
