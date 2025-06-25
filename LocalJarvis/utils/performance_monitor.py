"""
Sistema de Monitoramento de Performance para o Jarvis
Coleta métricas, gera relatórios e monitora saúde do sistema
"""

import psutil
import time
import threading
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import statistics

logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """Métricas do sistema."""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_total_gb: float
    disk_percent: float
    disk_used_gb: float
    disk_total_gb: float
    network_sent_mb: float
    network_recv_mb: float
    process_count: int
    thread_count: int
    uptime_hours: float

@dataclass
class ApplicationMetrics:
    """Métricas da aplicação."""
    timestamp: str
    requests_per_minute: int
    avg_response_time_ms: float
    active_sessions: int
    plugin_calls: int
    errors_per_minute: int
    cache_hit_rate: float
    model_inference_time_ms: float
    audio_processing_time_ms: float

@dataclass
class PerformanceAlert:
    """Alerta de performance."""
    timestamp: str
    severity: str  # INFO, WARNING, CRITICAL
    metric: str
    value: float
    threshold: float
    message: str

class PerformanceMonitor:
    """Monitor de performance do sistema e aplicação."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.metrics_file = "data/performance_metrics.json"
        self.alerts_file = "data/performance_alerts.json"
        
        # Configurações
        self.collection_interval = self.config.get('collection_interval', 60)  # segundos
        self.retention_days = self.config.get('retention_days', 7)
        self.enable_alerts = self.config.get('enable_alerts', True)
        
        # Thresholds para alertas
        self.thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_percent': 90.0,
            'response_time_ms': 2000.0,
            'error_rate': 5.0,  # errors per minute
        }
        self.thresholds.update(self.config.get('thresholds', {}))
        
        # Storage em memória
        self.system_metrics = deque(maxlen=1440)  # 24 horas com coleta por minuto
        self.app_metrics = deque(maxlen=1440)
        self.alerts = deque(maxlen=1000)
        
        # Contadores da aplicação
        self.request_count = 0
        self.response_times = deque(maxlen=100)
        self.error_count = 0
        self.plugin_calls = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.model_inference_times = deque(maxlen=50)
        self.audio_processing_times = deque(maxlen=50)
        
        # Controle de thread
        self.monitoring_active = False
        self.monitor_thread = None
        
        # Cria diretório de dados
        os.makedirs("data", exist_ok=True)
        
        # Carrega dados existentes
        self._load_historical_data()
        
        logger.info("PerformanceMonitor inicializado")
    
    def start_monitoring(self):
        """Inicia monitoramento em background."""
        if self.monitoring_active:
            logger.warning("Monitoramento já está ativo")
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        logger.info("Monitoramento de performance iniciado")
    
    def stop_monitoring(self):
        """Para monitoramento."""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        self._save_historical_data()
        logger.info("Monitoramento de performance parado")
    
    def _monitoring_loop(self):
        """Loop principal de monitoramento."""
        while self.monitoring_active:
            try:
                # Coleta métricas do sistema
                system_metrics = self._collect_system_metrics()
                self.system_metrics.append(system_metrics)
                
                # Coleta métricas da aplicação
                app_metrics = self._collect_app_metrics()
                self.app_metrics.append(app_metrics)
                
                # Verifica alertas
                if self.enable_alerts:
                    self._check_alerts(system_metrics, app_metrics)
                
                # Salva dados periodicamente
                if len(self.system_metrics) % 10 == 0:  # A cada 10 minutos
                    self._save_historical_data()
                
                time.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"Erro no loop de monitoramento: {e}")
                time.sleep(30)  # Aguarda mais tempo em caso de erro
    
    def _collect_system_metrics(self) -> SystemMetrics:
        """Coleta métricas do sistema."""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memória
            memory = psutil.virtual_memory()
            
            # Disco
            disk = psutil.disk_usage('/')
            
            # Rede
            network = psutil.net_io_counters()
            
            # Processos
            process_count = len(psutil.pids())
            
            # Threads (aproximação)
            thread_count = sum(p.num_threads() for p in psutil.process_iter() 
                             if p.pid != os.getpid())
            
            # Uptime
            boot_timestamp = psutil.boot_time()
            uptime_seconds = time.time() - boot_timestamp
            uptime_hours = uptime_seconds / 3600
            
            return SystemMetrics(
                timestamp=datetime.now().isoformat(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_gb=memory.used / (1024**3),
                memory_total_gb=memory.total / (1024**3),
                disk_percent=disk.percent,
                disk_used_gb=disk.used / (1024**3),
                disk_total_gb=disk.total / (1024**3),
                network_sent_mb=network.bytes_sent / (1024**2),
                network_recv_mb=network.bytes_recv / (1024**2),
                process_count=process_count,
                thread_count=thread_count,
                uptime_hours=uptime_hours
            )
        
        except Exception as e:
            logger.error(f"Erro ao coletar métricas do sistema: {e}")
            return SystemMetrics(
                timestamp=datetime.now().isoformat(),
                cpu_percent=0, memory_percent=0, memory_used_gb=0,
                memory_total_gb=0, disk_percent=0, disk_used_gb=0,
                disk_total_gb=0, network_sent_mb=0, network_recv_mb=0,
                process_count=0, thread_count=0, uptime_hours=0
            )
    
    def _collect_app_metrics(self) -> ApplicationMetrics:
        """Coleta métricas da aplicação."""
        try:
            # Calcula médias
            avg_response_time = (statistics.mean(self.response_times) 
                               if self.response_times else 0.0)
            
            cache_total = self.cache_hits + self.cache_misses
            cache_hit_rate = (self.cache_hits / cache_total * 100 
                            if cache_total > 0 else 0.0)
            
            avg_model_time = (statistics.mean(self.model_inference_times)
                            if self.model_inference_times else 0.0)
            
            avg_audio_time = (statistics.mean(self.audio_processing_times)
                            if self.audio_processing_times else 0.0)
            
            # Conta sessões ativas (mock - implementar integração real)
            active_sessions = 1  # Placeholder
            
            metrics = ApplicationMetrics(
                timestamp=datetime.now().isoformat(),
                requests_per_minute=self.request_count,
                avg_response_time_ms=avg_response_time,
                active_sessions=active_sessions,
                plugin_calls=self.plugin_calls,
                errors_per_minute=self.error_count,
                cache_hit_rate=cache_hit_rate,
                model_inference_time_ms=avg_model_time,
                audio_processing_time_ms=avg_audio_time
            )
            
            # Reset contadores
            self.request_count = 0
            self.error_count = 0
            self.plugin_calls = 0
            
            return metrics
        
        except Exception as e:
            logger.error(f"Erro ao coletar métricas da aplicação: {e}")
            return ApplicationMetrics(
                timestamp=datetime.now().isoformat(),
                requests_per_minute=0, avg_response_time_ms=0,
                active_sessions=0, plugin_calls=0,
                errors_per_minute=0, cache_hit_rate=0,
                model_inference_time_ms=0, audio_processing_time_ms=0
            )
    
    def _check_alerts(self, system_metrics: SystemMetrics, app_metrics: ApplicationMetrics):
        """Verifica se há alertas a serem gerados."""
        alerts = []
        
        # Alertas do sistema
        if system_metrics.cpu_percent > self.thresholds['cpu_percent']:
            alerts.append(PerformanceAlert(
                timestamp=datetime.now().isoformat(),
                severity="WARNING",
                metric="cpu_percent",
                value=system_metrics.cpu_percent,
                threshold=self.thresholds['cpu_percent'],
                message=f"Alto uso de CPU: {system_metrics.cpu_percent:.1f}%"
            ))
        
        if system_metrics.memory_percent > self.thresholds['memory_percent']:
            alerts.append(PerformanceAlert(
                timestamp=datetime.now().isoformat(),
                severity="WARNING",
                metric="memory_percent",
                value=system_metrics.memory_percent,
                threshold=self.thresholds['memory_percent'],
                message=f"Alto uso de memória: {system_metrics.memory_percent:.1f}%"
            ))
        
        if system_metrics.disk_percent > self.thresholds['disk_percent']:
            alerts.append(PerformanceAlert(
                timestamp=datetime.now().isoformat(),
                severity="CRITICAL",
                metric="disk_percent",
                value=system_metrics.disk_percent,
                threshold=self.thresholds['disk_percent'],
                message=f"Disco quase cheio: {system_metrics.disk_percent:.1f}%"
            ))
        
        # Alertas da aplicação
        if app_metrics.avg_response_time_ms > self.thresholds['response_time_ms']:
            alerts.append(PerformanceAlert(
                timestamp=datetime.now().isoformat(),
                severity="WARNING",
                metric="response_time_ms",
                value=app_metrics.avg_response_time_ms,
                threshold=self.thresholds['response_time_ms'],
                message=f"Tempo de resposta alto: {app_metrics.avg_response_time_ms:.1f}ms"
            ))
        
        if app_metrics.errors_per_minute > self.thresholds['error_rate']:
            alerts.append(PerformanceAlert(
                timestamp=datetime.now().isoformat(),
                severity="CRITICAL",
                metric="error_rate",
                value=app_metrics.errors_per_minute,
                threshold=self.thresholds['error_rate'],
                message=f"Alta taxa de erros: {app_metrics.errors_per_minute} erros/min"
            ))
        
        # Adiciona alertas à lista
        for alert in alerts:
            self.alerts.append(alert)
            logger.warning(f"Alerta de performance: {alert.message}")
    
    def _save_historical_data(self):
        """Salva dados históricos em arquivo."""
        try:
            # Salva métricas
            metrics_data = {
                'system_metrics': [asdict(m) for m in list(self.system_metrics)],
                'app_metrics': [asdict(m) for m in list(self.app_metrics)],
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.metrics_file, 'w', encoding='utf-8') as f:
                json.dump(metrics_data, f, indent=2, ensure_ascii=False)
            
            # Salva alertas
            alerts_data = {
                'alerts': [asdict(a) for a in list(self.alerts)],
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.alerts_file, 'w', encoding='utf-8') as f:
                json.dump(alerts_data, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"Erro ao salvar dados históricos: {e}")
    
    def _load_historical_data(self):
        """Carrega dados históricos."""
        try:
            # Carrega métricas
            if os.path.exists(self.metrics_file):
                with open(self.metrics_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Filtra dados recentes
                cutoff_time = datetime.now() - timedelta(days=self.retention_days)
                
                for metric_data in data.get('system_metrics', []):
                    try:
                        timestamp = datetime.fromisoformat(metric_data['timestamp'])
                        if timestamp > cutoff_time:
                            self.system_metrics.append(SystemMetrics(**metric_data))
                    except Exception:
                        continue
                
                for metric_data in data.get('app_metrics', []):
                    try:
                        timestamp = datetime.fromisoformat(metric_data['timestamp'])
                        if timestamp > cutoff_time:
                            self.app_metrics.append(ApplicationMetrics(**metric_data))
                    except Exception:
                        continue
            
            # Carrega alertas
            if os.path.exists(self.alerts_file):
                with open(self.alerts_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                cutoff_time = datetime.now() - timedelta(days=self.retention_days)
                
                for alert_data in data.get('alerts', []):
                    try:
                        timestamp = datetime.fromisoformat(alert_data['timestamp'])
                        if timestamp > cutoff_time:
                            self.alerts.append(PerformanceAlert(**alert_data))
                    except Exception:
                        continue
            
            logger.info(f"Carregados {len(self.system_metrics)} métricas de sistema e {len(self.alerts)} alertas")
        
        except Exception as e:
            logger.error(f"Erro ao carregar dados históricos: {e}")
    
    # Métodos para registrar eventos da aplicação
    def record_request(self, response_time_ms: float):
        """Registra uma requisição."""
        self.request_count += 1
        self.response_times.append(response_time_ms)
    
    def record_error(self):
        """Registra um erro."""
        self.error_count += 1
    
    def record_plugin_call(self):
        """Registra chamada de plugin."""
        self.plugin_calls += 1
    
    def record_cache_hit(self):
        """Registra cache hit."""
        self.cache_hits += 1
    
    def record_cache_miss(self):
        """Registra cache miss."""
        self.cache_misses += 1
    
    def record_model_inference(self, time_ms: float):
        """Registra tempo de inferência do modelo."""
        self.model_inference_times.append(time_ms)
    
    def record_audio_processing(self, time_ms: float):
        """Registra tempo de processamento de áudio."""
        self.audio_processing_times.append(time_ms)
    
    # Métodos para consultar dados
    def get_current_system_status(self) -> Dict[str, Any]:
        """Retorna status atual do sistema."""
        if not self.system_metrics:
            return {"status": "No data available"}
        
        latest = self.system_metrics[-1]
        return {
            "timestamp": latest.timestamp,
            "cpu_percent": latest.cpu_percent,
            "memory_percent": latest.memory_percent,
            "disk_percent": latest.disk_percent,
            "uptime_hours": latest.uptime_hours,
            "process_count": latest.process_count
        }
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retorna alertas recentes."""
        recent_alerts = list(self.alerts)[-limit:]
        return [asdict(alert) for alert in reversed(recent_alerts)]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Retorna resumo de performance."""
        if not self.system_metrics or not self.app_metrics:
            return {"status": "Insufficient data"}
        
        # Médias das últimas 24 horas
        recent_system = list(self.system_metrics)[-60:]  # Última hora
        recent_app = list(self.app_metrics)[-60:]
        
        avg_cpu = statistics.mean(m.cpu_percent for m in recent_system)
        avg_memory = statistics.mean(m.memory_percent for m in recent_system)
        avg_response_time = statistics.mean(m.avg_response_time_ms for m in recent_app)
        total_requests = sum(m.requests_per_minute for m in recent_app)
        total_errors = sum(m.errors_per_minute for m in recent_app)
        
        return {
            "period": "Last hour",
            "avg_cpu_percent": round(avg_cpu, 2),
            "avg_memory_percent": round(avg_memory, 2),
            "avg_response_time_ms": round(avg_response_time, 2),
            "total_requests": total_requests,
            "total_errors": total_errors,
            "error_rate_percent": round((total_errors / max(total_requests, 1)) * 100, 2),
            "alerts_count": len([a for a in self.alerts 
                               if datetime.fromisoformat(a.timestamp) > 
                               datetime.now() - timedelta(hours=1)])
        }
    
    def export_metrics(self, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Exporta métricas para um período específico."""
        try:
            start_dt = datetime.fromisoformat(start_date) if start_date else datetime.now() - timedelta(days=1)
            end_dt = datetime.fromisoformat(end_date) if end_date else datetime.now()
            
            # Filtra métricas por período
            filtered_system = []
            filtered_app = []
            filtered_alerts = []
            
            for metric in self.system_metrics:
                timestamp = datetime.fromisoformat(metric.timestamp)
                if start_dt <= timestamp <= end_dt:
                    filtered_system.append(asdict(metric))
            
            for metric in self.app_metrics:
                timestamp = datetime.fromisoformat(metric.timestamp)
                if start_dt <= timestamp <= end_dt:
                    filtered_app.append(asdict(metric))
            
            for alert in self.alerts:
                timestamp = datetime.fromisoformat(alert.timestamp)
                if start_dt <= timestamp <= end_dt:
                    filtered_alerts.append(asdict(alert))
            
            return {
                "export_period": {
                    "start": start_dt.isoformat(),
                    "end": end_dt.isoformat()
                },
                "system_metrics": filtered_system,
                "app_metrics": filtered_app,
                "alerts": filtered_alerts,
                "summary": {
                    "total_system_metrics": len(filtered_system),
                    "total_app_metrics": len(filtered_app),
                    "total_alerts": len(filtered_alerts)
                }
            }
        
        except Exception as e:
            logger.error(f"Erro ao exportar métricas: {e}")
            return {"error": str(e)}

# Instância global do monitor
performance_monitor = PerformanceMonitor()

# Funções de conveniência
def start_monitoring():
    """Inicia monitoramento de performance."""
    performance_monitor.start_monitoring()

def stop_monitoring():
    """Para monitoramento de performance."""
    performance_monitor.stop_monitoring()

def record_request(response_time_ms: float):
    """Registra requisição."""
    performance_monitor.record_request(response_time_ms)

def record_error():
    """Registra erro."""
    performance_monitor.record_error()

def record_plugin_call():
    """Registra chamada de plugin."""
    performance_monitor.record_plugin_call()

def get_system_status():
    """Retorna status do sistema."""
    return performance_monitor.get_current_system_status()

def get_performance_summary():
    """Retorna resumo de performance."""
    return performance_monitor.get_performance_summary()

def get_recent_alerts(limit: int = 10):
    """Retorna alertas recentes."""
    return performance_monitor.get_recent_alerts(limit)
