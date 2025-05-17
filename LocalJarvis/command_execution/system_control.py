import logging
import platform
import subprocess

logger = logging.getLogger(__name__)

class SystemControl:
    """Classe para controle avançado do sistema."""
    
    def __init__(self):
        self.platform = platform.system().lower()

    def shutdown(self):
        """Desliga o sistema."""
        try:
            if self.platform == 'windows':
                subprocess.run("shutdown /s /t 0", shell=True, check=True)
            else:
                subprocess.run("sudo shutdown -h now", shell=True, check=True)
            logger.info("Sistema desligado.")
            return "Sistema desligado."
        except subprocess.SubprocessError as e:
            logger.error(f"Erro ao desligar o sistema: {e}")
            return f"Erro: {str(e)}"

    def adjust_volume(self, level):
        """Ajusta o volume do sistema (exemplo para Windows)."""
        try:
            if self.platform == 'windows':
                subprocess.run(f"powershell -c (New-Object -ComObject WScript.Shell).SendKeys([char]175*{level})", shell=True, check=True)
                logger.info(f"Volume ajustado para nível {level}.")
                return f"Volume ajustado para {level}."
            else:
                logger.warning("Ajuste de volume não implementado para este SO.")
                return "Funcionalidade não suportada."
        except subprocess.SubprocessError as e:
            logger.error(f"Erro ao ajustar volume: {e}")
            return f"Erro: {str(e)}"
