import pytest
from audio_processing.speech_to_text import SpeechToText
from audio_processing.text_to_speech import TextToSpeech

def test_speech_to_text_init():
    stt = SpeechToText("http://whisper:5001")
    assert stt.docker_url == "http://whisper:5001"

def test_text_to_speech_init():
    tts = TextToSpeech("http://tts:5002")
    assert tts.docker_url == "http://tts:5002"

def test_text_to_speech_offline_fallback(monkeypatch):
    tts = TextToSpeech("http://tts:5002", offline=True)
    def fake_synthesize(text):
        return b"AUDIO_FAKE"
    monkeypatch.setattr(tts, "_synthesize_offline", fake_synthesize)
    result = tts.synthesize("Olá mundo")
    assert result == b"AUDIO_FAKE"

def test_speech_to_text_multilang():
    stt = SpeechToText("http://whisper:5001", timeout=10, language="en")
    assert stt.language == "en"
