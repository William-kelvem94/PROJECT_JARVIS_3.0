"""
Sistema de logging corrigido do JARVIS 3.0
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from colorama import Fore, Back, Style, init

# Inicializa colorama para Windows
init(autoreset=True)

class ColoredFormatter(logging.Formatter):
    """Formatter colorido para logs"""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Back.WHITE,
    }
    
    def format(self, record):
        # Aplica cor baseada no level
        color = self.COLORS.get(record.levelname, '')
        levelname_colored = f"{color}{record.levelname}{Style.RESET_ALL}"
        
        # Adiciona emoji baseado no level
        if record.levelname == 'DEBUG':
            levelname_colored = f"🔍 {levelname_colored}"
        elif record.levelname == 'INFO':
            levelname_colored = f"ℹ️ {levelname_colored}"
        elif record.levelname == 'WARNING':
            levelname_colored = f"⚠️ {levelname_colored}"
        elif record.levelname == 'ERROR':
            levelname_colored = f"❌ {levelname_colored}"
        elif record.levelname == 'CRITICAL':
            levelname_colored = f"💥 {levelname_colored}"
        
        # Substitui o levelname original
        record.levelname = levelname_colored
        
        return super().format(record)

def create_logger(name: str = "JARVIS", level: str = "INFO") -> logging.Logger:
    """
    Cria e configura um logger personalizado
    
    Args:
        name: Nome do logger
        level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    
    # Remove handlers existentes para evitar duplicação
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Define o nível
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Cria diretório de logs
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Formatter para console (colorido)
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    
    # Handler para arquivo
    log_file = logs_dir / f"jarvis_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)  # Arquivo sempre com DEBUG
    
    # Formatter para arquivo (sem cores)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s - [%(filename)s:%(lineno)d]',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    # Adiciona handlers ao logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    # Evita propagação para o root logger
    logger.propagate = False
    
    return logger

# Cria logger padrão
default_logger = create_logger("JARVIS", "INFO")

# Função compatível com versões anteriores
def setup_logger(name: str = "JARVIS", level: str = "INFO") -> logging.Logger:
    """Função compatível para setup de logger"""
    return create_logger(name, level)
