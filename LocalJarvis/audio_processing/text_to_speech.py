import requests
import logging
import pyttsx3
import io

logger = logging.getLogger(__name__)

class TextToSpeech:
    """Classe para síntese de texto em áudio usando gTTS via Docker ou pyttsx3 local."""
    
    def __init__(self, docker_url, voice='default', offline=False):
        self.docker_url = docker_url
        self.voice = voice
        self.offline = offline
        if offline:
            self.engine = pyttsx3.init()
            self.engine.setProperty('voice', voice)

    def synthesize(self, text):
        """Converte texto em áudio usando o serviço Docker ou pyttsx3."""
        if self.offline:
            try:
                self.engine.save_to_file(text, 'temp.wav')
                self.engine.runAndWait()
                with open('temp.wav', 'rb') as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Erro ao sintetizar áudio offline: {e}")
                raise
        try:
            response = requests.post(
                f"{self.docker_url}/synthesize",
                json={"text": text, "voice": self.voice},
                timeout=10
            )
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            logger.error(f"Erro ao sintetizar áudio: {e}")
            raise
