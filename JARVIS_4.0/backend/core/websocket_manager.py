"""
JARVIS 4.0 WebSocket Manager
Real-time communication handling
"""
from fastapi import WebSocket
from typing import List, Dict, Any
import json
import asyncio
from loguru import logger

class WebSocketManager:
    """Manages WebSocket connections and broadcasting"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str = None):
        """Accept and store new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if user_id:
            self.user_connections[user_id] = websocket
            
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket, user_id: str = None):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            
        if user_id and user_id in self.user_connections:
            del self.user_connections[user_id]
            
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send message to specific WebSocket"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def send_to_user(self, message: Dict[str, Any], user_id: str):
        """Send message to specific user"""
        if user_id in self.user_connections:
            websocket = self.user_connections[user_id]
            await self.send_personal_message(message, websocket)
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        if not self.active_connections:
            return
            
        disconnected = []
        for websocket in self.active_connections:
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected.append(websocket)
        
        # Remove disconnected clients
        for websocket in disconnected:
            self.disconnect(websocket)
    
    async def send_typing_indicator(self, user_id: str = None):
        """Send typing indicator"""
        message = {"type": "typing", "content": "JARVIS is thinking..."}
        
        if user_id:
            await self.send_to_user(message, user_id)
        else:
            await self.broadcast(message)
    
    async def send_system_status(self, status: Dict[str, Any]):
        """Send system status update"""
        message = {"type": "system_status", "content": status}
        await self.broadcast(message)
    
    def get_connection_count(self) -> int:
        """Get number of active connections"""
        return len(self.active_connections)