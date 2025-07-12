#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 3.0 - Sistema de Assistente Virtual Inteligente
Ponto de entrada principal do sistema
"""

import os
import sys
import logging
import argparse
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.append(str(Path(__file__).parent))

from core.app import JarvisApp
from core.config import Config
from utils.logger_fixed import default_logger, setup_logger

def main():
    """Função principal do sistema"""
    # Configuração de argumentos da linha de comando
    parser = argparse.ArgumentParser(description='JARVIS 3.0 - Assistente Virtual Inteligente')
    parser.add_argument('--mode', choices=['web', 'cli'], default='web', 
                       help='Modo de execução (web ou cli)')
    parser.add_argument('--debug', action='store_true', 
                       help='Executar em modo debug')
    parser.add_argument('--port', type=int, default=5000, 
                       help='Porta para o servidor web')
    parser.add_argument('--host', default='localhost', 
                       help='Host para o servidor web')
    
    args = parser.parse_args()
    
    # Setup do logger
    try:
        logger = setup_logger("JARVIS_MAIN", "DEBUG" if args.debug else "INFO")
        if args.debug:
            logger.setLevel(logging.DEBUG)
    except Exception:
        # Fallback logger se houver problemas
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("JARVIS_MAIN")
    
    try:
        # Carrega a configuração
        config = Config()
        
        # Inicializa a aplicação
        app = JarvisApp(config)
        
        logger.info("🚀 Iniciando JARVIS 3.0...")
        
        if args.mode == 'web':
            logger.info(f"🌐 Modo Web - Servidor iniciando em http://{args.host}:{args.port}")
            app.run_web_server(host=args.host, port=args.port, debug=args.debug)
        else:
            logger.info("💻 Modo CLI iniciado")
            app.run_cli()
            
    except KeyboardInterrupt:
        logger.info("👋 Sistema interrompido pelo usuário")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Erro crítico: {e}")
        if args.debug:
            raise
        sys.exit(1)

if __name__ == "__main__":
    main()
