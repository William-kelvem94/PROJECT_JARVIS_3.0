"""
Sistema de monitoramento de recursos do sistema
"""

import psutil
import time
import platform
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

@dataclass
class SystemInfo:
    """Informações do sistema"""
    cpu_percent: float
    memory_percent: float
    memory_used: float  # GB
    memory_total: float  # GB
    disk_percent: float
    disk_used: float  # GB
    disk_total: float  # GB
    network_sent: float  # MB/s
    network_recv: float  # MB/s
    boot_time: datetime
    uptime: float  # hours
    temperature: Optional[float] = None
    battery_percent: Optional[float] = None
    battery_plugged: Optional[bool] = None
    gpu_usage: Optional[List[Dict]] = None

class SystemMonitor:
    """Monitor de recursos do sistema"""
    
    def __init__(self):
        self.last_network = None
        self.last_network_time = None
        
    def get_cpu_info(self) -> Dict:
        """Obtém informações da CPU"""
        return {
            'percent': psutil.cpu_percent(interval=1),
            'count': psutil.cpu_count(),
            'frequency': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
            'per_cpu': psutil.cpu_percent(percpu=True)
        }
    
    def get_memory_info(self) -> Dict:
        """Obtém informações da memória"""
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            'total': round(memory.total / (1024**3), 2),  # GB
            'used': round(memory.used / (1024**3), 2),    # GB
            'free': round(memory.free / (1024**3), 2),    # GB
            'percent': memory.percent,
            'swap_total': round(swap.total / (1024**3), 2),
            'swap_used': round(swap.used / (1024**3), 2),
            'swap_percent': swap.percent
        }
    
    def get_disk_info(self) -> Dict:
        """Obtém informações do disco"""
        disk = psutil.disk_usage('/')
        
        return {
            'total': round(disk.total / (1024**3), 2),  # GB
            'used': round(disk.used / (1024**3), 2),    # GB
            'free': round(disk.free / (1024**3), 2),    # GB
            'percent': round((disk.used / disk.total) * 100, 2)
        }
    
    def get_network_info(self) -> Dict:
        """Obtém informações da rede"""
        current_time = time.time()
        network = psutil.net_io_counters()
        
        if self.last_network and self.last_network_time:
            time_delta = current_time - self.last_network_time
            bytes_sent = network.bytes_sent - self.last_network.bytes_sent
            bytes_recv = network.bytes_recv - self.last_network.bytes_recv
            
            speed_sent = round((bytes_sent / time_delta) / (1024**2), 2)  # MB/s
            speed_recv = round((bytes_recv / time_delta) / (1024**2), 2)  # MB/s
        else:
            speed_sent = 0
            speed_recv = 0
        
        self.last_network = network
        self.last_network_time = current_time
        
        return {
            'bytes_sent': round(network.bytes_sent / (1024**3), 2),  # GB
            'bytes_recv': round(network.bytes_recv / (1024**3), 2),  # GB
            'speed_sent': speed_sent,  # MB/s
            'speed_recv': speed_recv,  # MB/s
            'packets_sent': network.packets_sent,
            'packets_recv': network.packets_recv
        }
    
    def _extract_cpu_temperatures(self, temps: Dict) -> List[float]:
        """Extrai temperaturas da CPU dos sensores"""
        cpu_temps = []
        for name, entries in temps.items():
            for entry in entries:
                if 'cpu' in name.lower() or 'core' in name.lower():
                    cpu_temps.append(entry.current)
        return cpu_temps
    
    def get_temperature_info(self) -> Optional[Dict]:
        """Obtém informações de temperatura"""
        try:
            if not hasattr(psutil, "sensors_temperatures"):
                return None
                
            temps = psutil.sensors_temperatures()
            if not temps:
                return None
            
            cpu_temps = self._extract_cpu_temperatures(temps)
            if not cpu_temps:
                return None
                
            return {
                'cpu_temp': round(sum(cpu_temps) / len(cpu_temps), 1),
                'max_temp': max(cpu_temps),
                'sensors': temps
            }
        except Exception:
            return None
    
    def get_battery_info(self) -> Optional[Dict]:
        """Obtém informações da bateria"""
        try:
            battery = psutil.sensors_battery()
            if battery:
                return {
                    'percent': battery.percent,
                    'plugged': battery.power_plugged,
                    'time_left': battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else None
                }
        except Exception:
            pass
        return None
    
    def get_gpu_info(self) -> Optional[List[Dict]]:
        """Obtém informações da GPU"""
        if not GPU_AVAILABLE:
            return None
        
        try:
            gpus = GPUtil.getGPUs()
            gpu_info = []
            
            for gpu in gpus:
                gpu_info.append({
                    'id': gpu.id,
                    'name': gpu.name,
                    'load': round(gpu.load * 100, 1),
                    'memory_used': round(gpu.memoryUsed, 1),
                    'memory_total': round(gpu.memoryTotal, 1),
                    'memory_percent': round((gpu.memoryUsed / gpu.memoryTotal) * 100, 1),
                    'temperature': gpu.temperature
                })
            
            return gpu_info
        except Exception:
            return None
    
    def get_processes_info(self, limit: int = 10) -> List[Dict]:
        """Obtém informações dos processos que mais consomem recursos"""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Ordena por uso de CPU
        processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
        
        return processes[:limit]
    
    def get_system_info(self) -> SystemInfo:
        """Obtém informações completas do sistema"""
        # Informações básicas
        cpu_info = self.get_cpu_info()
        memory_info = self.get_memory_info()
        disk_info = self.get_disk_info()
        network_info = self.get_network_info()
        
        # Informações extras
        temp_info = self.get_temperature_info()
        battery_info = self.get_battery_info()
        gpu_info = self.get_gpu_info()
        
        # Boot time e uptime
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = (datetime.now() - boot_time).total_seconds() / 3600  # hours
        
        return SystemInfo(
            cpu_percent=cpu_info['percent'],
            memory_percent=memory_info['percent'],
            memory_used=memory_info['used'],
            memory_total=memory_info['total'],
            disk_percent=disk_info['percent'],
            disk_used=disk_info['used'],
            disk_total=disk_info['total'],
            network_sent=network_info['speed_sent'],
            network_recv=network_info['speed_recv'],
            boot_time=boot_time,
            uptime=round(uptime, 2),
            temperature=temp_info['cpu_temp'] if temp_info else None,
            battery_percent=battery_info['percent'] if battery_info else None,
            battery_plugged=battery_info['plugged'] if battery_info else None,
            gpu_usage=gpu_info
        )
    
    def get_system_overview(self) -> Dict:
        """Obtém uma visão geral do sistema"""
        return {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'hostname': platform.node(),
            'python_version': platform.python_version(),
            'cpu_count': psutil.cpu_count(),
            'cpu_count_logical': psutil.cpu_count(logical=True),
            'memory_total': round(psutil.virtual_memory().total / (1024**3), 2),
            'disk_total': round(psutil.disk_usage('/').total / (1024**3), 2),
            'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat()
        }
