import logging
import sys
import os
from logging.handlers import SysLogHandler

def setup_logger():
    """Configura o logger global com arquivo, console e syslog opcional."""
    logger = logging.getLogger("Jarvis")
    logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Handler para console
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # Handler para arquivo
    file_handler = logging.FileHandler('/app/logs/jarvis.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Handler syslog opcional (exemplo, descomente se usar syslog externo)
    # syslog_handler = SysLogHandler(address=('logs.papertrailapp.com', 12345))
    # logger.addHandler(syslog_handler)

    return logger
