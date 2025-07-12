"""
JARVIS 4.0 Voice API Routes
Speech-to-text and text-to-speech
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional
import asyncio

from core.ai_manager import AIManager

router = APIRouter()

class VoiceResponse(BaseModel):
    transcription: str
    text_response: str
    has_audio: bool
    timestamp: float

def get_ai_manager() -> AIManager:
    """Dependency to get AI manager"""
    from main import ai_manager as global_ai_manager
    if not global_ai_manager or not global_ai_manager.is_ready():
        raise HTTPException(status_code=503, detail="AI service not available")
    return global_ai_manager

@router.post("/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...),
    ai_manager: AIManager = Depends(get_ai_manager)
):
    """Transcribe audio to text using Whisper"""
    if not ai_manager.voice_module:
        raise HTTPException(status_code=503, detail="Voice module not available")
    
    try:
        # Read audio data
        audio_data = await audio.read()
        
        # Validate file size (50MB max)
        if len(audio_data) > 50 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="Audio file too large")
        
        # Transcribe
        transcription = await ai_manager.voice_module.transcribe_audio(audio_data)
        
        return {
            "transcription": transcription,
            "filename": audio.filename,
            "size": len(audio_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/speak")
async def text_to_speech(
    text: str,
    ai_manager: AIManager = Depends(get_ai_manager)
):
    """Convert text to speech"""
    if not ai_manager.voice_module:
        raise HTTPException(status_code=503, detail="Voice module not available")
    
    try:
        # Generate speech
        audio_data = await ai_manager.voice_module.generate_speech(text)
        
        if audio_data:
            return Response(
                content=audio_data,
                media_type="audio/wav",
                headers={"Content-Disposition": "attachment; filename=speech.wav"}
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to generate speech")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process", response_model=VoiceResponse)
async def process_voice(
    audio: UploadFile = File(...),
    user_id: Optional[str] = None,
    ai_manager: AIManager = Depends(get_ai_manager)
):
    """Process voice input (STT + Chat + TTS)"""
    if not ai_manager.voice_module:
        raise HTTPException(status_code=503, detail="Voice module not available")
    
    try:
        # Read audio data
        audio_data = await audio.read()
        
        # Process through voice pipeline
        result = await ai_manager.process_voice(audio_data, user_id)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return VoiceResponse(
            transcription=result["transcription"],
            text_response=result["text_response"],
            has_audio=result["audio_response"] is not None,
            timestamp=result["timestamp"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audio/{user_id}")
async def get_voice_response_audio(
    user_id: str,
    ai_manager: AIManager = Depends(get_ai_manager)
):
    """Get the audio response for the last voice interaction"""
    # This is a placeholder - in a real implementation, you'd store
    # the audio response temporarily and retrieve it here
    raise HTTPException(status_code=501, detail="Audio retrieval not yet implemented")

@router.get("/voices")
async def get_available_voices(
    ai_manager: AIManager = Depends(get_ai_manager)
):
    """Get available TTS voices"""
    if not ai_manager.voice_module:
        raise HTTPException(status_code=503, detail="Voice module not available")
    
    try:
        voice_info = ai_manager.voice_module.get_voice_info()
        return voice_info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/formats")
async def get_supported_formats(
    ai_manager: AIManager = Depends(get_ai_manager)
):
    """Get supported audio formats"""
    if not ai_manager.voice_module:
        raise HTTPException(status_code=503, detail="Voice module not available")
    
    try:
        formats = ai_manager.voice_module.get_supported_formats()
        return {"supported_formats": formats}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_voice_status(
    ai_manager: AIManager = Depends(get_ai_manager)
):
    """Get voice module status"""
    try:
        status = await ai_manager.get_status()
        return {
            "voice_available": status["modules"]["voice"],
            "whisper_model": status["models"]["whisper_model"],
            "ready": status["ready"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))