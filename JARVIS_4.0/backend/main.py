"""
JARVIS 4.0 - FastAPI Main Application
Modern AI Assistant with real-time capabilities
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from core.config import settings
from core.database import init_db
from core.ai_manager import AIManager
from core.websocket_manager import WebSocketManager
from api.routes import auth, chat, voice, vision, system
from utils.logger import setup_logger

# Setup logging
logger = setup_logger(__name__)

# Global managers
ai_manager = None
websocket_manager = WebSocketManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    global ai_manager
    
    # Startup
    logger.info("🚀 Starting JARVIS 4.0...")
    
    # Initialize database
    await init_db()
    
    # Initialize AI components
    ai_manager = AIManager()
    await ai_manager.initialize()
    
    logger.info("✅ JARVIS 4.0 ready!")
    
    yield
    
    # Shutdown
    logger.info("🔄 Shutting down JARVIS 4.0...")
    if ai_manager:
        await ai_manager.cleanup()

# Create FastAPI app
app = FastAPI(
    title="JARVIS 4.0 API",
    description="Next Generation AI Assistant",
    version="4.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(voice.router, prefix="/api/voice", tags=["Voice"])
app.include_router(vision.router, prefix="/api/vision", tags=["Vision"])
app.include_router(system.router, prefix="/api/system", tags=["System"])

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint for real-time communication"""
    await websocket_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            response = await handle_websocket_message(data)
            await websocket_manager.send_personal_message(response, websocket)
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

async def handle_websocket_message(data: dict) -> dict:
    """Handle incoming WebSocket messages"""
    message_type = data.get("type")
    content = data.get("content")
    
    if message_type == "chat":
        response = await ai_manager.process_text(content)
        return {"type": "chat_response", "content": response}
    elif message_type == "voice":
        # Handle voice input
        response = await ai_manager.process_voice(content)
        return {"type": "voice_response", "content": response}
    else:
        return {"type": "error", "content": "Unknown message type"}

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "4.0.0",
        "services": {
            "ai": ai_manager.is_ready() if ai_manager else False,
            "database": True,  # TODO: Check database connection
            "websocket": True
        }
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "🤖 JARVIS 4.0 - Next Generation AI Assistant",
        "version": "4.0.0",
        "docs": "/api/docs"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )