import logging
import sys

def setup_logger():
    """Configura o logger global."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('jarvis.log')
        ]
    )
