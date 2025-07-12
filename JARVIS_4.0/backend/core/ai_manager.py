"""
JARVIS 4.0 AI Manager
Central AI coordination with local models
"""
import asyncio
from typing import Optional, Dict, Any, List
from loguru import logger

from core.config import settings

# Optional imports for AI modules
try:
    from modules.voice_module import VoiceModule
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    logger.warning("Voice module dependencies not available")

try:
    from modules.vision_module import VisionModule
    VISION_AVAILABLE = True
except ImportError:
    VISION_AVAILABLE = False
    logger.warning("Vision module dependencies not available")

try:
    from modules.chat_module import ChatModule
    CHAT_AVAILABLE = True
except ImportError:
    CHAT_AVAILABLE = False
    logger.warning("Chat module dependencies not available")

class AIManager:
    """Centralized AI management system"""
    
    def __init__(self):
        self.chat_module: Optional[ChatModule] = None
        self.voice_module: Optional[VoiceModule] = None
        self.vision_module: Optional[VisionModule] = None
        self._ready = False
    
    async def initialize(self):
        """Initialize all AI components"""
        logger.info("🧠 Initializing AI Manager...")
        
        try:
            # Initialize chat module (Ollama)
            if CHAT_AVAILABLE:
                self.chat_module = ChatModule()
                await self.chat_module.initialize()
            else:
                logger.warning("Chat module not available")
            
            # Initialize voice module (Whisper + TTS)
            if settings.ENABLE_VOICE and VOICE_AVAILABLE:
                self.voice_module = VoiceModule()
                await self.voice_module.initialize()
            else:
                logger.warning("Voice module not available or disabled")
            
            # Initialize vision module (YOLO + OpenCV)
            if settings.ENABLE_VISION and VISION_AVAILABLE:
                self.vision_module = VisionModule()
                await self.vision_module.initialize()
            else:
                logger.warning("Vision module not available or disabled")
            
            self._ready = True
            logger.info("✅ AI Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize AI Manager: {e}")
            # Don't raise, continue with limited functionality
            self._ready = True  # Mark as ready even with limited functionality
    
    async def cleanup(self):
        """Cleanup AI resources"""
        logger.info("🧹 Cleaning up AI Manager...")
        
        if self.chat_module:
            await self.chat_module.cleanup()
        if self.voice_module:
            await self.voice_module.cleanup()
        if self.vision_module:
            await self.vision_module.cleanup()
        
        self._ready = False
        logger.info("✅ AI Manager cleanup complete")
    
    def is_ready(self) -> bool:
        """Check if AI Manager is ready"""
        return self._ready
    
    async def process_text(self, text: str, user_id: str = None) -> Dict[str, Any]:
        """Process text input through chat module"""
        if not self.chat_module:
            return {"error": "Chat module not available"}
        
        try:
            response = await self.chat_module.generate_response(text, user_id)
            return {
                "text": response,
                "type": "text_response",
                "timestamp": asyncio.get_event_loop().time()
            }
        except Exception as e:
            logger.error(f"Error processing text: {e}")
            return {"error": str(e)}
    
    async def process_voice(self, audio_data: bytes, user_id: str = None) -> Dict[str, Any]:
        """Process voice input (STT + Chat + TTS)"""
        if not self.voice_module:
            return {"error": "Voice module not available"}
        
        try:
            # Speech to Text
            transcription = await self.voice_module.transcribe_audio(audio_data)
            
            if not transcription.strip():
                return {"error": "No speech detected"}
            
            # Process through chat
            chat_response = await self.process_text(transcription, user_id)
            
            if "error" in chat_response:
                return chat_response
            
            # Text to Speech
            audio_response = await self.voice_module.generate_speech(chat_response["text"])
            
            return {
                "transcription": transcription,
                "text_response": chat_response["text"],
                "audio_response": audio_response,
                "type": "voice_response",
                "timestamp": asyncio.get_event_loop().time()
            }
            
        except Exception as e:
            logger.error(f"Error processing voice: {e}")
            return {"error": str(e)}
    
    async def process_image(self, image_data: bytes, task: str = "detect") -> Dict[str, Any]:
        """Process image through vision module"""
        if not self.vision_module:
            return {"error": "Vision module not available"}
        
        try:
            if task == "detect":
                results = await self.vision_module.detect_objects(image_data)
            elif task == "classify":
                results = await self.vision_module.classify_image(image_data)
            elif task == "face":
                results = await self.vision_module.detect_faces(image_data)
            else:
                return {"error": f"Unknown vision task: {task}"}
            
            return {
                "results": results,
                "task": task,
                "type": "vision_response",
                "timestamp": asyncio.get_event_loop().time()
            }
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return {"error": str(e)}
    
    async def get_status(self) -> Dict[str, Any]:
        """Get AI Manager status"""
        return {
            "ready": self._ready,
            "modules": {
                "chat": self.chat_module is not None and CHAT_AVAILABLE,
                "voice": self.voice_module is not None and VOICE_AVAILABLE,
                "vision": self.vision_module is not None and VISION_AVAILABLE,
            },
            "models": {
                "ollama_model": settings.OLLAMA_MODEL,
                "whisper_model": settings.WHISPER_MODEL,
                "yolo_model": settings.YOLO_MODEL
            },
            "availability": {
                "chat": CHAT_AVAILABLE,
                "voice": VOICE_AVAILABLE,
                "vision": VISION_AVAILABLE
            }
        }