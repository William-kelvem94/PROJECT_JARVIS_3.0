@echo off
echo.
echo ============================================================
echo  JARVIS 3.0 - INSTALACAO DA VERSAO DESKTOP
echo ============================================================
echo.

:: Verifica se Node.js está instalado
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js nao encontrado!
    echo 📥 Baixe e instale o Node.js em: https://nodejs.org/
    echo.
    pause
    exit /b 1
)

echo ✅ Node.js encontrado!
node --version

:: Verifica se Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python nao encontrado!
    echo 📥 Baixe e instale o Python em: https://python.org/
    echo.
    pause
    exit /b 1
)

echo ✅ Python encontrado!
python --version

echo.
echo 📦 Instalando dependencias do Electron...
cd /d "%~dp0"
npm install

if %errorlevel% neq 0 (
    echo ❌ Erro ao instalar dependencias!
    pause
    exit /b 1
)

echo.
echo ✅ Instalacao concluida!
echo.
echo 🚀 Para executar o JARVIS Desktop:
echo    npm start
echo.
echo 📦 Para criar um instalador:
echo    npm run dist
echo.
pause
