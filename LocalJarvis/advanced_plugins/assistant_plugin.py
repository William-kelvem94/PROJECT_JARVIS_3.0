"""
Plugin de Assistente Virtual e Chatbot Avançado
Funções: atendimento ao cliente, assistência pessoal, agenda, lembretes
"""

import json
import os
import re
import datetime
from typing import Dict, List, Optional, Any
import requests
import logging

logger = logging.getLogger(__name__)

class AssistantPlugin:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.reminders_file = "data/reminders.json"
        self.notes_file = "data/notes.json"
        self.contacts_file = "data/contacts.json"
        self.tasks_file = "data/tasks.json"
        
        # Cria diretório de dados se não existir
        os.makedirs("data", exist_ok=True)
        
        # Carrega dados existentes
        self.reminders = self._load_data(self.reminders_file, [])
        self.notes = self._load_data(self.notes_file, [])
        self.contacts = self._load_data(self.contacts_file, {})
        self.tasks = self._load_data(self.tasks_file, [])
        
        logger.info("AssistantPlugin inicializado com dados carregados")

    def _load_data(self, filename: str, default: Any) -> Any:
        """Carrega dados de arquivo JSON."""
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Erro ao carregar {filename}: {e}")
        return default

    def _save_data(self, filename: str, data: Any) -> bool:
        """Salva dados em arquivo JSON."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar {filename}: {e}")
            return False

    def process(self, text: str) -> Optional[str]:
        """Processa comandos do assistente pessoal."""
        text_lower = text.lower().strip()
        
        # Lembretes
        if any(word in text_lower for word in ['lembrar', 'lembrete', 'reminder']):
            return self._handle_reminder(text)
        
        # Notas
        elif any(word in text_lower for word in ['nota', 'anotar', 'note']):
            return self._handle_note(text)
        
        # Tarefas
        elif any(word in text_lower for word in ['tarefa', 'task', 'fazer', 'to-do']):
            return self._handle_task(text)
        
        # Contatos
        elif any(word in text_lower for word in ['contato', 'telefone', 'email', 'contact']):
            return self._handle_contact(text)
        
        # Agenda
        elif any(word in text_lower for word in ['agenda', 'compromisso', 'reunião', 'meeting']):
            return self._handle_schedule(text)
        
        # Pesquisa
        elif any(word in text_lower for word in ['pesquisar', 'search', 'procurar']):
            return self._handle_search(text)
        
        # Cálculos
        elif any(word in text_lower for word in ['calcular', 'calculate', 'quanto é']):
            return self._handle_calculation(text)
        
        # Clima (integração básica)
        elif any(word in text_lower for word in ['clima', 'tempo', 'weather']):
            return self._handle_weather(text)
        
        return None

    def _handle_reminder(self, text: str) -> str:
        """Gerencia lembretes."""
        if 'criar' in text.lower() or 'adicionar' in text.lower():
            return self._create_reminder(text)
        elif 'listar' in text.lower() or 'mostrar' in text.lower():
            return self._list_reminders()
        elif 'remover' in text.lower() or 'deletar' in text.lower():
            return self._remove_reminder(text)
        else:
            return "Comandos de lembrete: 'criar lembrete [texto]', 'listar lembretes', 'remover lembrete [id]'"

    def _create_reminder(self, text: str) -> str:
        """Cria um novo lembrete."""
        # Extrai texto do lembrete
        match = re.search(r'(?:criar|adicionar)\s+lembrete\s+(.+)', text, re.IGNORECASE)
        if not match:
            return "Por favor, especifique o texto do lembrete. Ex: 'criar lembrete comprar leite'"
        
        reminder_text = match.group(1)
        reminder_id = len(self.reminders) + 1
        
        # Tenta extrair data/hora (implementação básica)
        reminder_time = None
        time_patterns = [
            r'(?:em|daqui a)\s+(\d+)\s+(?:minutos?|mins?)',
            r'(?:em|daqui a)\s+(\d+)\s+(?:horas?|hrs?)',
            r'(?:às|at)\s+(\d{1,2}:\d{2})',
            r'(?:amanhã|tomorrow)',
            r'(?:hoje|today)'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                reminder_time = self._parse_time(match.group(0))
                break
        
        reminder = {
            'id': reminder_id,
            'text': reminder_text,
            'created_at': datetime.datetime.now().isoformat(),
            'reminder_time': reminder_time,
            'active': True
        }
        
        self.reminders.append(reminder)
        self._save_data(self.reminders_file, self.reminders)
        
        time_info = f" para {reminder_time}" if reminder_time else ""
        return f"✅ Lembrete #{reminder_id} criado{time_info}: {reminder_text}"

    def _list_reminders(self) -> str:
        """Lista lembretes ativos."""
        active_reminders = [r for r in self.reminders if r.get('active', True)]
        
        if not active_reminders:
            return "📝 Nenhum lembrete ativo encontrado."
        
        result = "📝 **Lembretes Ativos:**\n"
        for reminder in active_reminders:
            time_info = f" ({reminder.get('reminder_time', 'sem horário')})" if reminder.get('reminder_time') else ""
            result += f"#{reminder['id']}: {reminder['text']}{time_info}\n"
        
        return result

    def _remove_reminder(self, text: str) -> str:
        """Remove um lembrete."""
        match = re.search(r'(?:remover|deletar)\s+lembrete\s+#?(\d+)', text, re.IGNORECASE)
        if not match:
            return "Por favor, especifique o ID do lembrete. Ex: 'remover lembrete #1'"
        
        reminder_id = int(match.group(1))
        
        for reminder in self.reminders:
            if reminder['id'] == reminder_id:
                reminder['active'] = False
                self._save_data(self.reminders_file, self.reminders)
                return f"✅ Lembrete #{reminder_id} removido: {reminder['text']}"
        
        return f"❌ Lembrete #{reminder_id} não encontrado."

    def _handle_note(self, text: str) -> str:
        """Gerencia notas."""
        if 'criar' in text.lower() or 'anotar' in text.lower():
            return self._create_note(text)
        elif 'listar' in text.lower() or 'mostrar' in text.lower():
            return self._list_notes()
        elif 'buscar' in text.lower() or 'procurar' in text.lower():
            return self._search_notes(text)
        else:
            return "Comandos de nota: 'anotar [texto]', 'listar notas', 'buscar nota [termo]'"

    def _create_note(self, text: str) -> str:
        """Cria uma nova nota."""
        match = re.search(r'(?:criar|anotar)\s+(?:nota\s+)?(.+)', text, re.IGNORECASE)
        if not match:
            return "Por favor, especifique o conteúdo da nota."
        
        note_text = match.group(1)
        note_id = len(self.notes) + 1
        
        note = {
            'id': note_id,
            'text': note_text,
            'created_at': datetime.datetime.now().isoformat(),
            'tags': self._extract_tags(note_text)
        }
        
        self.notes.append(note)
        self._save_data(self.notes_file, self.notes)
        
        return f"📝 Nota #{note_id} criada: {note_text}"

    def _list_notes(self) -> str:
        """Lista todas as notas."""
        if not self.notes:
            return "📝 Nenhuma nota encontrada."
        
        result = "📝 **Suas Notas:**\n"
        for note in self.notes[-10:]:  # Últimas 10 notas
            created = datetime.datetime.fromisoformat(note['created_at']).strftime("%d/%m %H:%M")
            result += f"#{note['id']} ({created}): {note['text'][:50]}...\n"
        
        return result

    def _handle_task(self, text: str) -> str:
        """Gerencia tarefas."""
        if 'criar' in text.lower() or 'adicionar' in text.lower():
            return self._create_task(text)
        elif 'listar' in text.lower():
            return self._list_tasks()
        elif 'concluir' in text.lower() or 'finalizar' in text.lower():
            return self._complete_task(text)
        else:
            return "Comandos de tarefa: 'criar tarefa [texto]', 'listar tarefas', 'concluir tarefa #[id]'"

    def _handle_calculation(self, text: str) -> str:
        """Realiza cálculos básicos."""
        try:
            # Extrai expressão matemática básica
            import re
            
            # Substitui palavras por operadores
            text = text.lower()
            text = re.sub(r'\bmais\b', '+', text)
            text = re.sub(r'\bmenos\b', '-', text)
            text = re.sub(r'\bvezes\b|\bmultiplicado por\b', '*', text)
            text = re.sub(r'\bdividido por\b', '/', text)
            
            # Extrai números e operadores
            match = re.search(r'([\d\+\-\*/\.\(\)\s]+)', text)
            if match:
                expression = match.group(1).strip()
                # Avalia expressão de forma segura
                result = eval(expression)
                return f"🧮 Resultado: {expression} = {result}"
            
            return "❌ Não consegui identificar a expressão matemática."
        
        except Exception as e:
            return f"❌ Erro no cálculo: {str(e)}"

    def _handle_weather(self, text: str) -> str:
        """Informações básicas sobre clima."""
        # Esta é uma implementação básica - pode ser expandida com API real
        return "🌤️ Para informações detalhadas sobre o clima, use o plugin de clima específico."

    def _handle_search(self, text: str) -> str:
        """Realiza pesquisas básicas."""
        match = re.search(r'pesquisar\s+(.+)', text, re.IGNORECASE)
        if match:
            query = match.group(1)
            return f"🔍 Você pode pesquisar '{query}' usando:\n" \
                   f"• Google: https://google.com/search?q={query.replace(' ', '+')}\n" \
                   f"• Wikipedia: https://pt.wikipedia.org/wiki/{query.replace(' ', '_')}"
        
        return "Por favor, especifique o que deseja pesquisar."

    def _extract_tags(self, text: str) -> List[str]:
        """Extrai tags de um texto."""
        # Implementação básica - pode ser melhorada com NLP 
        tags = re.findall(r'#(\w+)', text)
        return tags

    def _parse_time(self, time_str: str) -> str:
        """Converte string de tempo em timestamp."""
        # Implementação básica - pode ser expandida
        now = datetime.datetime.now()
        
        if 'minuto' in time_str:
            minutes = int(re.search(r'(\d+)', time_str).group(1))
            target_time = now + datetime.timedelta(minutes=minutes)
        elif 'hora' in time_str:
            hours = int(re.search(r'(\d+)', time_str).group(1))
            target_time = now + datetime.timedelta(hours=hours)
        elif 'amanhã' in time_str:
            target_time = now + datetime.timedelta(days=1)
        else:
            target_time = now
        
        return target_time.isoformat()

    def customer_service(self, question: str) -> str:
        """Atende perguntas de clientes com respostas mais inteligentes."""
        faq = {
            'horário': 'Nosso horário de atendimento é de segunda a sexta, das 8h às 18h.',
            'contato': 'Você pode entrar em contato conosco pelo email suporte@empresa.com ou telefone (11) 1234-5678.',
            'produto': 'Nossos produtos incluem soluções de IA, automação e assistentes virtuais.',
            'preço': 'Para informações sobre preços, por favor entre em contato com nossa equipe comercial.',
            'suporte': 'Nossa equipe de suporte está disponível para ajudá-lo com qualquer dúvida técnica.'
        }
        
        question_lower = question.lower()
        for key, answer in faq.items():
            if key in question_lower:
                return f"🤝 {answer}"
        
        return "🤝 Obrigado pela sua pergunta. Nossa equipe entrará em contato em breve."

    def personal_assistant(self, request: str) -> str:
        """Auxilia em tarefas pessoais de forma mais avançada."""
        request_lower = request.lower()
        
        if 'agenda' in request_lower or 'compromisso' in request_lower:
            return self._handle_schedule(request)
        elif 'lembrar' in request_lower:
            return self._handle_reminder(request)
        elif 'nota' in request_lower:
            return self._handle_note(request)
        elif 'pesquisar' in request_lower:
            return self._handle_search(request)
        else:
            return f"📋 Posso ajudar com: agenda, lembretes, notas, pesquisas e muito mais. Como posso te auxiliar?"

    def _handle_schedule(self, text: str) -> str:
        """Gerencia compromissos da agenda."""
        return "📅 Funcionalidade de agenda em desenvolvimento. Em breve você poderá gerenciar seus compromissos!"

    def _create_task(self, text: str) -> str:
        """Cria uma nova tarefa."""
        match = re.search(r'(?:criar|adicionar)\s+tarefa\s+(.+)', text, re.IGNORECASE)
        if not match:
            return "Por favor, especifique a tarefa. Ex: 'criar tarefa estudar Python'"
        
        task_text = match.group(1)
        task_id = len(self.tasks) + 1
        
        task = {
            'id': task_id,
            'text': task_text,
            'created_at': datetime.datetime.now().isoformat(),
            'completed': False,
            'priority': 'normal'
        }
        
        self.tasks.append(task)
        self._save_data(self.tasks_file, self.tasks)
        
        return f"✅ Tarefa #{task_id} criada: {task_text}"

    def _list_tasks(self) -> str:
        """Lista tarefas pendentes."""
        pending_tasks = [t for t in self.tasks if not t.get('completed', False)]
        
        if not pending_tasks:
            return "✅ Parabéns! Você não tem tarefas pendentes."
        
        result = "📋 **Tarefas Pendentes:**\n"
        for task in pending_tasks:
            result += f"#{task['id']}: {task['text']}\n"
        
        return result

    def _complete_task(self, text: str) -> str:
        """Marca tarefa como concluída."""
        match = re.search(r'(?:concluir|finalizar)\s+tarefa\s+#?(\d+)', text, re.IGNORECASE)
        if not match:
            return "Por favor, especifique o ID da tarefa. Ex: 'concluir tarefa #1'"
        
        task_id = int(match.group(1))
        
        for task in self.tasks:
            if task['id'] == task_id:
                task['completed'] = True
                task['completed_at'] = datetime.datetime.now().isoformat()
                self._save_data(self.tasks_file, self.tasks)
                return f"🎉 Tarefa #{task_id} concluída: {task['text']}"
        
        return f"❌ Tarefa #{task_id} não encontrada."

    def _search_notes(self, text: str) -> str:
        """Busca notas por termo."""
        match = re.search(r'buscar\s+nota\s+(.+)', text, re.IGNORECASE)
        if not match:
            return "Por favor, especifique o termo de busca."
        
        search_term = match.group(1).lower()
        found_notes = []
        
        for note in self.notes:
            if search_term in note['text'].lower():
                found_notes.append(note)
        
        if not found_notes:
            return f"❌ Nenhuma nota encontrada com o termo '{search_term}'."
        
        result = f"🔍 **Notas encontradas para '{search_term}':**\n"
        for note in found_notes:
            result += f"#{note['id']}: {note['text'][:50]}...\n"
        
        return result

    def _handle_contact(self, text: str) -> str:
        """Gerencia contatos."""
        if 'adicionar' in text.lower() or 'criar' in text.lower():
            return self._add_contact(text)
        elif 'buscar' in text.lower() or 'procurar' in text.lower():
            return self._search_contact(text)
        elif 'listar' in text.lower():
            return self._list_contacts()
        else:
            return "Comandos de contato: 'adicionar contato [nome] [telefone]', 'buscar contato [nome]', 'listar contatos'"

    def _add_contact(self, text: str) -> str:
        """Adiciona um novo contato."""
        # Implementação básica para adicionar contatos
        return "📞 Funcionalidade de contatos em desenvolvimento!"

    def _search_contact(self, text: str) -> str:
        """Busca um contato."""
        return "📞 Funcionalidade de busca de contatos em desenvolvimento!"

    def _list_contacts(self) -> str:
        """Lista todos os contatos."""
        return "📞 Funcionalidade de listagem de contatos em desenvolvimento!"
