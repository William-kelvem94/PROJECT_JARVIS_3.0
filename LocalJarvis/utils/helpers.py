import re

def sanitize_command(command):
    """Remove caracteres perigosos de comandos."""
    return re.sub(r'[;&|]', '', command)
