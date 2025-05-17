import subprocess
import logging
import platform

logger = logging.getLogger(__name__)

class ProgramExecutor:
    """Classe para executar comandos do sistema com segurança."""
    
    def __init__(self, allowed_commands):
        self.allowed_commands = allowed_commands
        self.platform = platform.system().lower()

    def execute(self, command):
        """Executa um comando do sistema, se permitido."""
        try:
            if command not in self.allowed_commands:
                logger.warning(f"Comando '{command}' não permitido.")
                return "Comando não permitido."
            
            # Ajusta comandos para compatibilidade com o sistema operacional
            if self.platform == 'windows':
                shell = True
            else:
                shell = False
                command = command.replace('cmd.exe /c ', '')

            result = subprocess.run(
                command,
                shell=shell,
                capture_output=True,
                text=True,
                timeout=10
            )
            logger.info(f"Comando '{command}' executado com sucesso.")
            return result.stdout or "Comando executado com sucesso."
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout ao executar comando: {command}")
            return "Erro: Comando expirou."
        except subprocess.SubprocessError as e:
            logger.error(f"Erro ao executar comando '{command}': {e}")
            return f"Erro: {str(e)}"
