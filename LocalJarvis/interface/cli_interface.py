import logging

logger = logging.getLogger(__name__)

def run_cli(jarvis):
    """Executa a interface CLI."""
    while True:
        try:
            user_input = input("Você: ")
            if user_input.lower() in ['exit', 'sair']:
                logger.info("CLI encerrado pelo usuário.")
                break
            response = jarvis.process_input(user_input, 'text')
            print(f"Jarvis: {response}")
        except KeyboardInterrupt:
            logger.info("CLI encerrado por interrupção.")
            break
        except Exception as e:
            logger.error(f"Erro no CLI: {e}")
            print(f"Erro: {str(e)}")
