"""
JARVIS 4.0 Voice Module  
Whisper STT + TTS integration
"""
import asyncio
import tempfile
import os
import io
from typing import Optional, Dict, Any
from loguru import logger

from core.config import settings

# Optional imports for voice processing
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    logger.warning("Whisper not available - Voice module will have limited functionality")

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    logger.warning("pyttsx3 not available - TTS will not work")

try:
    import soundfile as sf
    import numpy as np
    AUDIO_PROCESSING_AVAILABLE = True
except ImportError:
    AUDIO_PROCESSING_AVAILABLE = False
    logger.warning("Audio processing libraries not available")

class VoiceModule:
    """Voice processing with Whisper STT and TTS"""
    
    def __init__(self):
        self.whisper_model: Optional = None
        self.tts_engine: Optional = None
    
    async def initialize(self):
        """Initialize voice components"""
        logger.info("🎤 Initializing Voice Module...")
        
        # Initialize Whisper model
        if WHISPER_AVAILABLE:
            try:
                logger.info(f"Loading Whisper model: {settings.WHISPER_MODEL}")
                self.whisper_model = whisper.load_model(settings.WHISPER_MODEL)
                logger.info("✅ Whisper model loaded")
            except Exception as e:
                logger.error(f"❌ Failed to load Whisper: {e}")
        else:
            logger.warning("⚠️ Whisper not available")
        
        # Initialize TTS engine
        if PYTTSX3_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                
                # Configure TTS settings
                voices = self.tts_engine.getProperty('voices')
                if voices:
                    # Try to find a good voice (prefer female for JARVIS)
                    for i, voice in enumerate(voices):
                        if 'zira' in voice.name.lower() or 'hazel' in voice.name.lower():
                            self.tts_engine.setProperty('voice', voice.id)
                            break
                        elif i == 1 and len(voices) > 1:  # Use second voice if available
                            self.tts_engine.setProperty('voice', voice.id)
                
                # Set speech rate and volume
                self.tts_engine.setProperty('rate', 180)  # Slightly faster
                self.tts_engine.setProperty('volume', 0.9)
                
                logger.info("✅ TTS engine initialized")
                
            except Exception as e:
                logger.error(f"❌ Failed to initialize TTS: {e}")
                # TTS is optional, continue without it
        else:
            logger.warning("⚠️ pyttsx3 not available")
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.tts_engine:
            try:
                self.tts_engine.stop()
            except:
                pass
    
    async def transcribe_audio(self, audio_data: bytes) -> str:
        """Transcribe audio to text using Whisper"""
        if not self.whisper_model or not WHISPER_AVAILABLE:
            return "Voice transcription not available - Whisper model not loaded"
        
        try:
            # Save audio data to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name
            
            try:
                # Transcribe using Whisper
                result = self.whisper_model.transcribe(temp_path)
                transcription = result["text"].strip()
                
                logger.info(f"Transcribed: {transcription}")
                return transcription
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise
    
    async def generate_speech(self, text: str) -> Optional[bytes]:
        """Generate speech from text using TTS"""
        if not self.tts_engine or not PYTTSX3_AVAILABLE:
            logger.warning("TTS engine not available")
            return None
        
        try:
            # Create temporary file for audio output
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name
            
            try:
                # Generate speech to file
                self.tts_engine.save_to_file(text, temp_path)
                self.tts_engine.runAndWait()
                
                # Read generated audio file
                with open(temp_path, "rb") as audio_file:
                    audio_data = audio_file.read()
                
                logger.info(f"Generated speech for: {text[:50]}...")
                return audio_data
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            return None
    
    async def process_voice_command(self, audio_data: bytes) -> Dict[str, Any]:
        """Process complete voice command (STT + intent recognition)"""
        try:
            # Transcribe audio
            transcription = await self.transcribe_audio(audio_data)
            
            if not transcription.strip():
                return {"error": "No speech detected"}
            
            # Basic intent recognition
            intent = self._recognize_intent(transcription)
            
            return {
                "transcription": transcription,
                "intent": intent,
                "confidence": 0.8  # Placeholder confidence score
            }
            
        except Exception as e:
            logger.error(f"Error processing voice command: {e}")
            return {"error": str(e)}
    
    def _recognize_intent(self, text: str) -> str:
        """Basic intent recognition from text"""
        text_lower = text.lower()
        
        # Greeting intents
        if any(word in text_lower for word in ["hello", "hi", "hey", "good morning", "good evening"]):
            return "greeting"
        
        # Question intents
        if any(word in text_lower for word in ["what", "how", "when", "where", "why", "who"]):
            return "question"
        
        # Command intents
        if any(word in text_lower for word in ["open", "start", "launch", "run", "execute"]):
            return "command"
        
        # Time intents
        if any(word in text_lower for word in ["time", "date", "today", "now"]):
            return "time_query"
        
        # System intents
        if any(word in text_lower for word in ["status", "system", "health", "performance"]):
            return "system_query"
        
        return "general"
    
    def get_supported_formats(self) -> list:
        """Get supported audio formats"""
        return ["wav", "mp3", "flac", "m4a", "ogg"]
    
    def get_voice_info(self) -> Dict[str, Any]:
        """Get information about available voices"""
        if not self.tts_engine:
            return {"error": "TTS engine not available"}
        
        try:
            voices = self.tts_engine.getProperty('voices')
            current_voice = self.tts_engine.getProperty('voice')
            
            voice_info = []
            for voice in voices:
                voice_info.append({
                    "id": voice.id,
                    "name": voice.name,
                    "languages": getattr(voice, 'languages', []),
                    "gender": getattr(voice, 'gender', 'unknown'),
                    "age": getattr(voice, 'age', 'unknown'),
                    "current": voice.id == current_voice
                })
            
            return {
                "voices": voice_info,
                "current_voice": current_voice,
                "rate": self.tts_engine.getProperty('rate'),
                "volume": self.tts_engine.getProperty('volume')
            }
            
        except Exception as e:
            logger.error(f"Error getting voice info: {e}")
            return {"error": str(e)}