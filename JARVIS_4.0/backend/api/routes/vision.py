"""
JARVIS 4.0 Vision API Routes  
Computer vision with YOLO and OpenCV
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from core.ai_manager import AIManager

router = APIRouter()

class VisionResult(BaseModel):
    objects: List[Dict[str, Any]]
    task: str
    timestamp: float
    image_size: tuple

def get_ai_manager() -> AIManager:
    """Dependency to get AI manager"""
    from main import ai_manager as global_ai_manager
    if not global_ai_manager or not global_ai_manager.is_ready():
        raise HTTPException(status_code=503, detail="AI service not available")
    return global_ai_manager

@router.post("/detect")
async def detect_objects(
    image: UploadFile = File(...),
    ai_manager: AIManager = Depends(get_ai_manager)
):
    """Detect objects in image using YOLO"""
    if not ai_manager.vision_module:
        raise HTTPException(status_code=503, detail="Vision module not available")
    
    try:
        image_data = await image.read()
        result = await ai_manager.process_image(image_data, "detect")
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/classify")
async def classify_image(
    image: UploadFile = File(...),
    ai_manager: AIManager = Depends(get_ai_manager)
):
    """Classify image content"""
    # Placeholder implementation
    return {"message": "Vision classification coming soon", "status": "not_implemented"}

@router.post("/faces")
async def detect_faces(
    image: UploadFile = File(...),
    ai_manager: AIManager = Depends(get_ai_manager)
):
    """Detect faces in image"""
    # Placeholder implementation
    return {"message": "Face detection coming soon", "status": "not_implemented"}

@router.get("/status")
async def get_vision_status(ai_manager: AIManager = Depends(get_ai_manager)):
    """Get vision module status"""
    try:
        status = await ai_manager.get_status()
        return {
            "vision_available": status["modules"]["vision"],
            "yolo_model": status["models"]["yolo_model"],
            "ready": status["ready"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))