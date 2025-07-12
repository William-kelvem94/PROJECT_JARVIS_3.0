"""
JARVIS 4.0 System API Routes
System monitoring and management
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any
import psutil
import platform
import asyncio

from core.ai_manager import AIManager
from api.routes.auth import get_current_user

router = APIRouter()

class SystemStatus(BaseModel):
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    uptime: float
    platform: str
    python_version: str

def get_ai_manager() -> AIManager:
    """Dependency to get AI manager"""
    from main import ai_manager as global_ai_manager
    if not global_ai_manager or not global_ai_manager.is_ready():
        raise HTTPException(status_code=503, detail="AI service not available")
    return global_ai_manager

@router.get("/status", response_model=SystemStatus)
async def get_system_status():
    """Get system performance metrics"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        boot_time = psutil.boot_time()
        current_time = asyncio.get_event_loop().time()
        
        return SystemStatus(
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            disk_percent=disk.percent,
            uptime=current_time - boot_time,
            platform=platform.platform(),
            python_version=platform.python_version()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check(ai_manager: AIManager = Depends(get_ai_manager)):
    """Comprehensive health check"""
    try:
        ai_status = await ai_manager.get_status()
        
        return {
            "status": "healthy",
            "timestamp": asyncio.get_event_loop().time(),
            "services": {
                "api": True,
                "ai_manager": ai_status["ready"],
                "chat_module": ai_status["modules"]["chat"],
                "voice_module": ai_status["modules"]["voice"],
                "vision_module": ai_status["modules"]["vision"]
            },
            "models": ai_status["models"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics")
async def get_detailed_metrics(current_user: dict = Depends(get_current_user)):
    """Get detailed system metrics (authenticated)"""
    try:
        # CPU details
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        # Memory details
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Disk details
        disk_partitions = psutil.disk_partitions()
        disk_usage = []
        for partition in disk_partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_usage.append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": (usage.used / usage.total) * 100
                })
            except PermissionError:
                continue
        
        # Network details
        network_io = psutil.net_io_counters()
        
        return {
            "cpu": {
                "count": cpu_count,
                "frequency": cpu_freq._asdict() if cpu_freq else None,
                "percent": psutil.cpu_percent(interval=1, percpu=True)
            },
            "memory": {
                "virtual": memory._asdict(),
                "swap": swap._asdict()
            },
            "disk": disk_usage,
            "network": network_io._asdict() if network_io else None,
            "processes": len(psutil.pids())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/restart")
async def restart_services(
    service: str,
    current_user: dict = Depends(get_current_user),
    ai_manager: AIManager = Depends(get_ai_manager)
):
    """Restart specific services"""
    try:
        if service == "ai":
            await ai_manager.cleanup()
            await ai_manager.initialize()
            return {"message": "AI services restarted", "service": service}
        else:
            return {"error": f"Unknown service: {service}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs")
async def get_system_logs(
    lines: int = 100,
    current_user: dict = Depends(get_current_user)
):
    """Get system logs"""
    try:
        # Placeholder for log retrieval
        return {
            "logs": [
                {"timestamp": "2024-01-01T00:00:00Z", "level": "INFO", "message": "JARVIS 4.0 started"},
                {"timestamp": "2024-01-01T00:01:00Z", "level": "INFO", "message": "AI Manager initialized"}
            ],
            "total_lines": 2,
            "requested_lines": lines
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))