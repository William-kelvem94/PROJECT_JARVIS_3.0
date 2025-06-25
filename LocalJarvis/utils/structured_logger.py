"""
Sistema de Logging Estruturado para o Jarvis
Fornece logging avançado com rotação, níveis e formatação JSON
"""

import logging
import logging.handlers
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional
import traceback
import threading

class StructuredLogger:
    """Logger estruturado com formatação JSON e recursos avançados."""
    
    def __init__(self, 
                 name: str = "jarvis",
                 log_dir: str = "logs",
                 max_bytes: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5,
                 console_level: str = "INFO",
                 file_level: str = "DEBUG"):
        
        self.name = name
        self.log_dir = log_dir
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        
        # Cria diretório de logs
        os.makedirs(log_dir, exist_ok=True)
        
        # Configuração do logger principal
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Remove handlers existentes para evitar duplicação
        self.logger.handlers.clear()
        
        # Configuração de handlers
        self._setup_file_handler(file_level)
        self._setup_console_handler(console_level)
        self._setup_error_handler()
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Estatísticas
        self.stats = {
            'debug': 0,
            'info': 0,
            'warning': 0,
            'error': 0,
            'critical': 0
        }
    
    def _setup_file_handler(self, level: str):
        """Configura handler para arquivo com rotação."""
        file_path = os.path.join(self.log_dir, f"{self.name}.log")
        
        file_handler = logging.handlers.RotatingFileHandler(
            file_path,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(JSONFormatter())
        
        self.logger.addHandler(file_handler)
    
    def _setup_console_handler(self, level: str):
        """Configura handler para console."""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        console_handler.setFormatter(ColoredFormatter())
        
        self.logger.addHandler(console_handler)
    
    def _setup_error_handler(self):
        """Configura handler específico para erros."""
        error_path = os.path.join(self.log_dir, f"{self.name}_errors.log")
        
        error_handler = logging.handlers.RotatingFileHandler(
            error_path,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(JSONFormatter())
        
        self.logger.addHandler(error_handler)
    
    def _log_with_context(self, level: str, message: str, **kwargs):
        """Log com contexto adicional."""
        with self._lock:
            self.stats[level.lower()] += 1
            
            extra_data = {
                'timestamp': datetime.now().isoformat(),
                'level': level,
                'thread': threading.current_thread().name,
                'module': kwargs.pop('module', 'unknown'),
                'function': kwargs.pop('function', 'unknown'),
                **kwargs
            }
            
            # Adiciona traceback para erros
            if level in ['ERROR', 'CRITICAL']:
                extra_data['traceback'] = traceback.format_exc()
            
            getattr(self.logger, level.lower())(message, extra=extra_data)
    
    def debug(self, message: str, **kwargs):
        """Log de debug."""
        self._log_with_context('DEBUG', message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log de informação."""
        self._log_with_context('INFO', message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log de aviso."""
        self._log_with_context('WARNING', message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log de erro."""
        self._log_with_context('ERROR', message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log crítico."""
        self._log_with_context('CRITICAL', message, **kwargs)
    
    def log_user_interaction(self, user_input: str, response: str, processing_time: float = None):
        """Log específico para interações do usuário."""
        self.info(
            "User interaction",
            event_type="user_interaction",
            user_input=user_input[:100] + "..." if len(user_input) > 100 else user_input,
            response_length=len(response),
            processing_time=processing_time,
            module="jarvis_core"
        )
    
    def log_plugin_activity(self, plugin_name: str, action: str, success: bool, details: str = None):
        """Log específico para atividade de plugins."""
        level = 'INFO' if success else 'WARNING'
        self._log_with_context(
            level,
            f"Plugin {plugin_name}: {action}",
            event_type="plugin_activity",
            plugin_name=plugin_name,
            action=action,
            success=success,
            details=details,
            module="plugin_manager"
        )
    
    def log_system_event(self, event: str, severity: str = "INFO", **kwargs):
        """Log de eventos do sistema."""
        self._log_with_context(
            severity,
            event,
            event_type="system_event",
            **kwargs
        )
    
    def log_performance_metric(self, metric_name: str, value: float, unit: str = "ms"):
        """Log de métricas de performance."""
        self.info(
            f"Performance metric: {metric_name}",
            event_type="performance_metric",
            metric_name=metric_name,
            value=value,
            unit=unit,
            module="performance"
        )
    
    def log_security_event(self, event: str, severity: str = "WARNING", **kwargs):
        """Log de eventos de segurança."""
        self._log_with_context(
            severity,
            f"Security event: {event}",
            event_type="security_event",
            security_event=event,
            **kwargs
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de logging."""
        with self._lock:
            return {
                'total_logs': sum(self.stats.values()),
                'by_level': self.stats.copy(),
                'log_directory': self.log_dir,
                'logger_name': self.name
            }
    
    def export_logs(self, output_file: str, level: str = "INFO", limit: int = 1000):
        """Exporta logs para arquivo."""
        try:
            log_file = os.path.join(self.log_dir, f"{self.name}.log")
            
            if not os.path.exists(log_file):
                return False
            
            exported_logs = []
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Filtra por nível e limite
            count = 0
            for line in reversed(lines):  # Mais recentes primeiro
                if count >= limit:
                    break
                
                try:
                    log_entry = json.loads(line.strip())
                    if self._should_include_log(log_entry, level):
                        exported_logs.append(log_entry)
                        count += 1
                except json.JSONDecodeError:
                    continue
            
            # Salva logs exportados
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(exported_logs, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            self.error(f"Erro ao exportar logs: {e}")
            return False
    
    def _should_include_log(self, log_entry: Dict, min_level: str) -> bool:
        """Verifica se log deve ser incluído baseado no nível."""
        level_priority = {
            'DEBUG': 10,
            'INFO': 20,
            'WARNING': 30,
            'ERROR': 40,
            'CRITICAL': 50
        }
        
        log_level = log_entry.get('level', 'INFO')
        return level_priority.get(log_level, 20) >= level_priority.get(min_level, 20)


class JSONFormatter(logging.Formatter):
    """Formatador JSON para logs estruturados."""
    
    def format(self, record):
        """Formata registro como JSON."""
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'logger': record.name,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Adiciona dados extras se disponíveis
        if hasattr(record, '__dict__'):
            for key, value in record.__dict__.get('extra', {}).items():
                if key not in log_entry:
                    log_entry[key] = value
        
        return json.dumps(log_entry, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """Formatador colorido para console."""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    
    RESET = '\033[0m'
    
    def format(self, record):
        """Formata registro com cores."""
        color = self.COLORS.get(record.levelname, '')
        
        # Formato básico
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S')
        
        formatted = f"{color}[{timestamp}] {record.levelname:<8}{self.RESET} "
        formatted += f"{record.name} - {record.getMessage()}"
        
        # Adiciona contexto extra se disponível
        if hasattr(record, 'module') and record.module != 'unknown':
            formatted += f" [{record.module}]"
        
        return formatted


# Instância global do logger
jarvis_logger = StructuredLogger()

# Funções de conveniência
def debug(message: str, **kwargs):
    """Log de debug."""
    jarvis_logger.debug(message, **kwargs)

def info(message: str, **kwargs):
    """Log de informação."""
    jarvis_logger.info(message, **kwargs)

def warning(message: str, **kwargs):
    """Log de aviso."""
    jarvis_logger.warning(message, **kwargs)

def error(message: str, **kwargs):
    """Log de erro."""
    jarvis_logger.error(message, **kwargs)

def critical(message: str, **kwargs):
    """Log crítico."""
    jarvis_logger.critical(message, **kwargs)

def log_user_interaction(user_input: str, response: str, processing_time: float = None):
    """Log de interação do usuário."""
    jarvis_logger.log_user_interaction(user_input, response, processing_time)

def log_plugin_activity(plugin_name: str, action: str, success: bool, details: str = None):
    """Log de atividade de plugin."""
    jarvis_logger.log_plugin_activity(plugin_name, action, success, details)

def log_system_event(event: str, severity: str = "INFO", **kwargs):
    """Log de evento do sistema."""
    jarvis_logger.log_system_event(event, severity, **kwargs)

def log_performance_metric(metric_name: str, value: float, unit: str = "ms"):
    """Log de métrica de performance."""
    jarvis_logger.log_performance_metric(metric_name, value, unit)

def log_security_event(event: str, severity: str = "WARNING", **kwargs):
    """Log de evento de segurança."""
    jarvis_logger.log_security_event(event, severity, **kwargs)
