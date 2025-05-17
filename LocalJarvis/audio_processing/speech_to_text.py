import requests
import logging

logger = logging.getLogger(__name__)

class SpeechToText:
    """Classe para transcrição de áudio em texto usando Whisper via Docker."""
    
    def __init__(self, docker_url, timeout=10, language='pt'):
        self.docker_url = docker_url
        self.timeout = timeout
        self.language = language

    def transcribe(self, audio_data):
        """Transcreve áudio para texto usando o serviço Docker."""
        try:
            response = requests.post(
                f"{self.docker_url}/transcribe",
                files={"file": ("audio.wav", audio_data, "audio/wav")},
                data={"language": self.language},
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()['text']
        except requests.RequestException as e:
            logger.error(f"Erro ao transcrever áudio: {e}")
            raise
