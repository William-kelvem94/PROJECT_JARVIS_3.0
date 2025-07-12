"""
Sistema de plugins do JARVIS 3.0
"""

import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

class PluginManager:
    """Gerenciador de plugins do JARVIS"""
    
    def __init__(self):
        self.plugins = {}
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        # Inicializa plugins básicos
        self.init_basic_plugins()
    
    def init_basic_plugins(self):
        """Inicializa plugins básicos"""
        self.plugins = {
            'notes': NotesPlugin(),
            'reminders': RemindersPlugin(),
            'tasks': TasksPlugin(),
            'system': SystemPlugin()
        }
    
    def get_plugin(self, name: str):
        """Retorna um plugin pelo nome"""
        return self.plugins.get(name)
    
    def list_plugins(self) -> List[str]:
        """Lista todos os plugins disponíveis"""
        return list(self.plugins.keys())

class BasePlugin:
    """Classe base para plugins"""
    
    def __init__(self, name: str):
        self.name = name
        self.data_file = Path(f"data/{name}.json")
        self.data = self.load_data()
    
    def load_data(self) -> Dict:
        """Carrega dados do plugin"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}
    
    def save_data(self) -> bool:
        """Salva dados do plugin"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

class NotesPlugin(BasePlugin):
    """Plugin para anotações"""
    
    def __init__(self):
        super().__init__('notes')
        if 'notes' not in self.data:
            self.data['notes'] = []
    
    def add_note(self, content: str, title: str = None) -> bool:
        """Adiciona uma nova anotação"""
        note = {
            'id': len(self.data['notes']) + 1,
            'title': title or f"Nota {len(self.data['notes']) + 1}",
            'content': content,
            'created_at': datetime.now().isoformat()
        }
        self.data['notes'].append(note)
        return self.save_data()
    
    def list_notes(self) -> List[Dict]:
        """Lista todas as anotações"""
        return self.data['notes']
    
    def delete_note(self, note_id: int) -> bool:
        """Remove uma anotação"""
        self.data['notes'] = [n for n in self.data['notes'] if n['id'] != note_id]
        return self.save_data()

class RemindersPlugin(BasePlugin):
    """Plugin para lembretes"""
    
    def __init__(self):
        super().__init__('reminders')
        if 'reminders' not in self.data:
            self.data['reminders'] = []
    
    def add_reminder(self, message: str, datetime_str: str) -> bool:
        """Adiciona um lembrete"""
        try:
            reminder_time = datetime.fromisoformat(datetime_str)
            reminder = {
                'id': len(self.data['reminders']) + 1,
                'message': message,
                'datetime': reminder_time.isoformat(),
                'completed': False,
                'created_at': datetime.now().isoformat()
            }
            self.data['reminders'].append(reminder)
            return self.save_data()
        except ValueError:
            return False
    
    def list_reminders(self, pending_only: bool = True) -> List[Dict]:
        """Lista lembretes"""
        if pending_only:
            return [r for r in self.data['reminders'] if not r['completed']]
        return self.data['reminders']
    
    def complete_reminder(self, reminder_id: int) -> bool:
        """Marca lembrete como concluído"""
        for reminder in self.data['reminders']:
            if reminder['id'] == reminder_id:
                reminder['completed'] = True
                return self.save_data()
        return False

class TasksPlugin(BasePlugin):
    """Plugin para tarefas"""
    
    def __init__(self):
        super().__init__('tasks')
        if 'tasks' not in self.data:
            self.data['tasks'] = []
    
    def add_task(self, title: str, description: str = "", priority: str = "medium") -> bool:
        """Adiciona uma tarefa"""
        task = {
            'id': len(self.data['tasks']) + 1,
            'title': title,
            'description': description,
            'priority': priority,  # low, medium, high
            'completed': False,
            'created_at': datetime.now().isoformat()
        }
        self.data['tasks'].append(task)
        return self.save_data()
    
    def list_tasks(self, completed: bool = False) -> List[Dict]:
        """Lista tarefas"""
        return [t for t in self.data['tasks'] if t['completed'] == completed]
    
    def complete_task(self, task_id: int) -> bool:
        """Marca tarefa como concluída"""
        for task in self.data['tasks']:
            if task['id'] == task_id:
                task['completed'] = True
                task['completed_at'] = datetime.now().isoformat()
                return self.save_data()
        return False

class SystemPlugin(BasePlugin):
    """Plugin para comandos do sistema"""
    
    def __init__(self):
        super().__init__('system')
    
    def get_system_info(self) -> Dict:
        """Retorna informações do sistema"""
        import psutil
        import platform
        
        return {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'cpu_count': psutil.cpu_count(),
            'memory_total': round(psutil.virtual_memory().total / (1024**3), 2),
            'python_version': platform.python_version()
        }
    
    def get_quick_stats(self) -> Dict:
        """Retorna estatísticas rápidas"""
        import psutil
        
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:').percent,
            'timestamp': datetime.now().isoformat()
        }

# Instância global do gerenciador
plugin_manager = PluginManager()
