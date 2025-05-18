"""
Entrypoint local para rodar o Jarvis em modo CLI ou Web.
"""
import logging
from jarvis_entrypoint import Jarvis
from interface.cli_interface import run_cli

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Escolha o modo de execução:")
    print("1 - CLI (terminal)")
    print("2 - Web (Flask)")
    modo = input("Modo [1/2]: ").strip()
    if modo == "1":
        jarvis = Jarvis()
        run_cli(jarvis)
    elif modo == "2":
        from jarvis_entrypoint import app
        print("Acesse http://localhost:5000 no navegador.")
        app.run(host="0.0.0.0", port=5000, debug=True)
    else:
        print("Modo inválido.")
