"""
JARVIS 4.0 Chat Module
Local LLM integration with Ollama
"""
import asyncio
from typing import Optional, Dict, Any, List
from loguru import logger

from core.config import settings

# Optional httpx import
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    logger.warning("httpx not available - Chat module will have limited functionality")

class ChatModule:
    """Chat module using local Ollama LLM"""
    
    def __init__(self):
        self.client: Optional[httpx.AsyncClient] = None
        self.model = settings.OLLAMA_MODEL
        self.conversation_history: Dict[str, List[Dict]] = {}
    
    async def initialize(self):
        """Initialize Ollama connection"""
        logger.info("🗨️ Initializing Chat Module...")
        
        if not HTTPX_AVAILABLE:
            logger.warning("⚠️ httpx not available. Chat module will use fallback responses.")
            return
        
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # Test Ollama connection
        try:
            response = await self.client.get(f"{settings.OLLAMA_URL}/api/tags")
            if response.status_code == 200:
                models = response.json()
                logger.info(f"✅ Ollama connected. Available models: {[m['name'] for m in models.get('models', [])]}")
            else:
                logger.warning("⚠️ Ollama not responding. Install and start Ollama for local LLM support.")
        except Exception as e:
            logger.warning(f"⚠️ Could not connect to Ollama: {e}")
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.client:
            await self.client.aclose()
    
    async def generate_response(self, prompt: str, user_id: str = None) -> str:
        """Generate response using local LLM"""
        if not HTTPX_AVAILABLE or not self.client:
            # Fallback response when Ollama is not available
            return f"I understand you said: '{prompt}'. However, my local LLM is not currently available. Please ensure Ollama is installed and running to get AI-powered responses."
        
        try:
            # Prepare conversation context
            messages = self._prepare_messages(prompt, user_id)
            
            # Call Ollama API
            response = await self.client.post(
                f"{settings.OLLAMA_URL}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 1000
                    }
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get("message", {}).get("content", "Sorry, I couldn't generate a response.")
                
                # Store in conversation history
                if user_id:
                    self._add_to_history(user_id, "user", prompt)
                    self._add_to_history(user_id, "assistant", ai_response)
                
                return ai_response
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return "I'm having trouble connecting to my language model. Please try again."
                
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I encountered an error while processing your request."
    
    def _prepare_messages(self, prompt: str, user_id: str = None) -> List[Dict]:
        """Prepare messages for LLM with context"""
        messages = [
            {
                "role": "system",
                "content": """You are JARVIS, an advanced AI assistant inspired by Tony Stark's AI. 
                You are intelligent, helpful, and have a sophisticated personality. 
                You can help with various tasks including coding, analysis, research, and general conversation.
                Keep responses concise but informative. Be professional yet approachable."""
            }
        ]
        
        # Add conversation history
        if user_id and user_id in self.conversation_history:
            history = self.conversation_history[user_id][-10:]  # Last 10 messages
            messages.extend(history)
        
        # Add current prompt
        messages.append({"role": "user", "content": prompt})
        
        return messages
    
    def _add_to_history(self, user_id: str, role: str, content: str):
        """Add message to conversation history"""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        self.conversation_history[user_id].append({
            "role": role,
            "content": content
        })
        
        # Keep only last 20 messages per user
        if len(self.conversation_history[user_id]) > 20:
            self.conversation_history[user_id] = self.conversation_history[user_id][-20:]
    
    def clear_history(self, user_id: str):
        """Clear conversation history for user"""
        if user_id in self.conversation_history:
            del self.conversation_history[user_id]
    
    async def get_available_models(self) -> List[str]:
        """Get list of available Ollama models"""
        if not HTTPX_AVAILABLE or not self.client:
            return []
        
        try:
            response = await self.client.get(f"{settings.OLLAMA_URL}/api/tags")
            if response.status_code == 200:
                models = response.json()
                return [m['name'] for m in models.get('models', [])]
        except Exception as e:
            logger.error(f"Error getting models: {e}")
        
        return []