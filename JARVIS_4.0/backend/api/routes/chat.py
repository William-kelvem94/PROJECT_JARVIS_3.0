"""
JARVIS 4.0 Chat API Routes
Real-time chat with local LLM
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio

from core.ai_manager import AIManager

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    user_id: Optional[str] = None
    timestamp: float
    type: str = "text"

# Global AI manager instance (will be injected)
ai_manager: Optional[AIManager] = None

def get_ai_manager() -> AIManager:
    """Dependency to get AI manager"""
    from main import ai_manager as global_ai_manager
    if not global_ai_manager or not global_ai_manager.is_ready():
        raise HTTPException(status_code=503, detail="AI service not available")
    return global_ai_manager

@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    ai_manager: AIManager = Depends(get_ai_manager)
):
    """Send a message to JARVIS and get response"""
    try:
        result = await ai_manager.process_text(request.message, request.user_id)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return ChatResponse(
            response=result["text"],
            user_id=request.user_id,
            timestamp=result["timestamp"],
            type=result["type"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{user_id}")
async def get_chat_history(
    user_id: str,
    ai_manager: AIManager = Depends(get_ai_manager)
):
    """Get chat history for a user"""
    try:
        if ai_manager.chat_module and hasattr(ai_manager.chat_module, 'conversation_history'):
            history = ai_manager.chat_module.conversation_history.get(user_id, [])
            return {"history": history, "user_id": user_id}
        else:
            return {"history": [], "user_id": user_id}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/history/{user_id}")
async def clear_chat_history(
    user_id: str,
    ai_manager: AIManager = Depends(get_ai_manager)
):
    """Clear chat history for a user"""
    try:
        if ai_manager.chat_module:
            ai_manager.chat_module.clear_history(user_id)
        return {"message": "History cleared", "user_id": user_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models")
async def get_available_models(
    ai_manager: AIManager = Depends(get_ai_manager)
):
    """Get available LLM models"""
    try:
        if ai_manager.chat_module:
            models = await ai_manager.chat_module.get_available_models()
            return {"models": models}
        else:
            return {"models": []}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_chat_status(
    ai_manager: AIManager = Depends(get_ai_manager)
):
    """Get chat module status"""
    try:
        status = await ai_manager.get_status()
        return {
            "chat_available": status["modules"]["chat"],
            "current_model": status["models"]["ollama_model"],
            "ready": status["ready"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))