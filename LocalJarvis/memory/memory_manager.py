import sqlite3
import logging
import threading

logger = logging.getLogger(__name__)

class MemoryManager:
    """Classe para gerenciamento de memória e contexto com SQLite."""
    
    def __init__(self, db_path, user_id='default'):
        self.db_path = db_path
        self.user_id = user_id
        self.lock = threading.Lock()
        self._is_memory = (db_path == ':memory:')
        self.conn = None
        self._init_db()

    def _init_db(self):
        """Inicializa o banco de dados SQLite."""
        try:
            with self.lock:
                if self._is_memory:
                    self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
                    conn = self.conn
                else:
                    conn = sqlite3.connect(self.db_path)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS interactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT,
                        user_text TEXT,
                        assistant_response TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
                if not self._is_memory:
                    conn.close()
                logger.info("Banco de dados inicializado.")
        except sqlite3.Error as e:
            logger.error(f"Erro ao inicializar banco de dados: {e}")
            raise

    def store_interaction(self, user_text, assistant_response):
        """Armazena uma interação no banco de dados."""
        try:
            with self.lock:
                if self._is_memory:
                    conn = self.conn
                else:
                    conn = sqlite3.connect(self.db_path)
                conn.execute(
                    "INSERT INTO interactions (user_id, user_text, assistant_response) VALUES (?, ?, ?)",
                    (self.user_id, user_text, assistant_response)
                )
                conn.commit()
                if not self._is_memory:
                    conn.close()
                logger.debug("Interação armazenada.")
        except sqlite3.Error as e:
            logger.error(f"Erro ao armazenar interação: {e}")
            raise

    def get_context(self):
        """Recupera o contexto das últimas 5 interações do usuário."""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.execute(
                    "SELECT user_text, assistant_response FROM interactions WHERE user_id = ? ORDER BY id DESC LIMIT 5",
                    (self.user_id,)
                )
                context = "\n".join(
                    f"Usuário: {row[0]}\nAssistente: {row[1]}" for row in cursor
                )
                conn.close()
                return context or "Nenhum contexto disponível."
        except sqlite3.Error as e:
            logger.error(f"Erro ao recuperar contexto: {e}")
            return ""
