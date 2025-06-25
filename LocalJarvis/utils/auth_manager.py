"""
Sistema de Autenticação para o Jarvis
Fornece autenticação básica, controle de sessão e rate limiting
"""

import hashlib
import secrets
import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple
import jwt
from functools import wraps
from flask import request, jsonify, session
import logging

logger = logging.getLogger(__name__)

class AuthenticationManager:
    """Gerenciador de autenticação do Jarvis."""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.users_file = "data/users.json"
        self.sessions_file = "data/sessions.json"
        self.rate_limit_file = "data/rate_limits.json"
        
        # Configurações
        self.secret_key = self.config.get('secret_key', self._generate_secret_key())
        self.jwt_secret = self.config.get('jwt_secret_key', self._generate_secret_key())
        self.session_timeout = self.config.get('session_timeout_minutes', 30)
        self.max_login_attempts = self.config.get('max_login_attempts', 5)
        self.rate_limit_per_minute = self.config.get('rate_limit_per_minute', 60)
        
        # Cria diretório de dados
        os.makedirs("data", exist_ok=True)
        
        # Carrega dados
        self.users = self._load_users()
        self.sessions = self._load_sessions()
        self.rate_limits = self._load_rate_limits()
        
        # Cria usuário admin padrão se não existir
        if not self.users:
            self._create_default_admin()
        
        logger.info("AuthenticationManager inicializado")
    
    def _generate_secret_key(self) -> str:
        """Gera chave secreta aleatória."""
        return secrets.token_hex(32)
    
    def _load_users(self) -> Dict:
        """Carrega usuários do arquivo."""
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar usuários: {e}")
        return {}
    
    def _save_users(self):
        """Salva usuários no arquivo."""
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erro ao salvar usuários: {e}")
    
    def _load_sessions(self) -> Dict:
        """Carrega sessões ativas."""
        try:
            if os.path.exists(self.sessions_file):
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    sessions = json.load(f)
                    # Remove sessões expiradas
                    return self._clean_expired_sessions(sessions)
        except Exception as e:
            logger.error(f"Erro ao carregar sessões: {e}")
        return {}
    
    def _save_sessions(self):
        """Salva sessões no arquivo."""
        try:
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(self.sessions, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erro ao salvar sessões: {e}")
    
    def _load_rate_limits(self) -> Dict:
        """Carrega dados de rate limiting."""
        try:
            if os.path.exists(self.rate_limit_file):
                with open(self.rate_limit_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar rate limits: {e}")
        return {}
    
    def _save_rate_limits(self):
        """Salva dados de rate limiting."""
        try:
            with open(self.rate_limit_file, 'w', encoding='utf-8') as f:
                json.dump(self.rate_limits, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erro ao salvar rate limits: {e}")
    
    def _create_default_admin(self):
        """Cria usuário admin padrão."""
        default_password = "jarvis123"
        hashed_password = self._hash_password(default_password)
        
        self.users["admin"] = {
            "username": "admin",
            "password_hash": hashed_password,
            "role": "admin",
            "created_at": datetime.now().isoformat(),
            "last_login": None,
            "login_attempts": 0,
            "locked_until": None,
            "permissions": ["all"]
        }
        
        self._save_users()
        logger.warning(f"Usuário admin criado com senha padrão: {default_password}")
    
    def _hash_password(self, password: str) -> str:
        """Gera hash da senha com salt."""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', 
                                          password.encode('utf-8'), 
                                          salt.encode('utf-8'), 
                                          100000)
        return f"{salt}:{password_hash.hex()}"
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verifica se a senha está correta."""
        try:
            salt, stored_hash = password_hash.split(':')
            password_hash_check = hashlib.pbkdf2_hmac('sha256',
                                                    password.encode('utf-8'),
                                                    salt.encode('utf-8'),
                                                    100000)
            return password_hash_check.hex() == stored_hash
        except Exception as e:
            logger.error(f"Erro na verificação de senha: {e}")
            return False
    
    def _clean_expired_sessions(self, sessions: Dict) -> Dict:
        """Remove sessões expiradas."""
        now = datetime.now()
        valid_sessions = {}
        
        for session_id, session_data in sessions.items():
            try:
                expires_at = datetime.fromisoformat(session_data['expires_at'])
                if expires_at > now:
                    valid_sessions[session_id] = session_data
            except Exception:
                continue
        
        return valid_sessions
    
    def create_user(self, username: str, password: str, role: str = "user", 
                   permissions: List[str] = None) -> bool:
        """Cria um novo usuário."""
        try:
            if username in self.users:
                return False
            
            password_hash = self._hash_password(password)
            
            self.users[username] = {
                "username": username,
                "password_hash": password_hash,
                "role": role,
                "created_at": datetime.now().isoformat(),
                "last_login": None,
                "login_attempts": 0,
                "locked_until": None,
                "permissions": permissions or ["basic"]
            }
            
            self._save_users()
            logger.info(f"Usuário criado: {username}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar usuário: {e}")
            return False
    
    def authenticate(self, username: str, password: str, 
                    client_ip: str = None) -> Tuple[bool, str, Dict]:
        """Autentica usuário."""
        try:
            # Verifica rate limiting
            if not self._check_rate_limit(client_ip or "unknown"):
                return False, "Rate limit exceeded", {}
            
            # Verifica se usuário existe
            if username not in self.users:
                self._log_failed_attempt(username, client_ip)
                return False, "Invalid credentials", {}
            
            user = self.users[username]
            
            # Verifica se conta está bloqueada
            if self._is_account_locked(user):
                return False, "Account locked", {}
            
            # Verifica senha
            if not self._verify_password(password, user['password_hash']):
                self._handle_failed_login(username)
                return False, "Invalid credentials", {}
            
            # Login bem-sucedido
            self._handle_successful_login(username)
            session_token = self._create_session(username)
            
            return True, "Authentication successful", {
                "session_token": session_token,
                "user": {
                    "username": username,
                    "role": user['role'],
                    "permissions": user['permissions']
                }
            }
            
        except Exception as e:
            logger.error(f"Erro na autenticação: {e}")
            return False, "Authentication error", {}
    
    def _check_rate_limit(self, client_identifier: str) -> bool:
        """Verifica rate limiting."""
        now = time.time()
        minute_window = int(now / 60)
        
        if client_identifier not in self.rate_limits:
            self.rate_limits[client_identifier] = {}
        
        client_limits = self.rate_limits[client_identifier]
        
        # Remove janelas antigas
        old_windows = [w for w in client_limits.keys() if int(w) < minute_window - 5]
        for window in old_windows:
            del client_limits[window]
        
        # Verifica limite atual
        current_requests = client_limits.get(str(minute_window), 0)
        
        if current_requests >= self.rate_limit_per_minute:
            return False
        
        # Incrementa contador
        client_limits[str(minute_window)] = current_requests + 1
        self._save_rate_limits()
        
        return True
    
    def _is_account_locked(self, user: Dict) -> bool:
        """Verifica se conta está bloqueada."""
        if user.get('locked_until'):
            try:
                locked_until = datetime.fromisoformat(user['locked_until'])
                if datetime.now() < locked_until:
                    return True
                else:
                    # Remove bloqueio expirado
                    user['locked_until'] = None
                    user['login_attempts'] = 0
                    self._save_users()
            except Exception:
                pass
        
        return False
    
    def _handle_failed_login(self, username: str):
        """Lida com tentativa de login falhada."""
        user = self.users[username]
        user['login_attempts'] = user.get('login_attempts', 0) + 1
        
        if user['login_attempts'] >= self.max_login_attempts:
            # Bloqueia conta por 30 minutos
            lock_duration = timedelta(minutes=30)
            user['locked_until'] = (datetime.now() + lock_duration).isoformat()
            logger.warning(f"Conta bloqueada por tentativas excessivas: {username}")
        
        self._save_users()
    
    def _handle_successful_login(self, username: str):
        """Lida com login bem-sucedido."""
        user = self.users[username]
        user['last_login'] = datetime.now().isoformat()
        user['login_attempts'] = 0
        user['locked_until'] = None
        
        self._save_users()
        logger.info(f"Login bem-sucedido: {username}")
    
    def _log_failed_attempt(self, username: str, client_ip: str):
        """Registra tentativa de login falhada."""
        logger.warning(f"Tentativa de login falhada: {username} de {client_ip}")
    
    def _create_session(self, username: str) -> str:
        """Cria sessão para usuário."""
        session_id = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(minutes=self.session_timeout)
        
        self.sessions[session_id] = {
            "username": username,
            "created_at": datetime.now().isoformat(),
            "expires_at": expires_at.isoformat(),
            "last_activity": datetime.now().isoformat()
        }
        
        self._save_sessions()
        return session_id
    
    def validate_session(self, session_token: str) -> Tuple[bool, Optional[str]]:
        """Valida sessão."""
        try:
            if session_token not in self.sessions:
                return False, None
            
            session_data = self.sessions[session_token]
            expires_at = datetime.fromisoformat(session_data['expires_at'])
            
            if datetime.now() > expires_at:
                # Sessão expirada
                del self.sessions[session_token]
                self._save_sessions()
                return False, None
            
            # Atualiza última atividade
            session_data['last_activity'] = datetime.now().isoformat()
            self._save_sessions()
            
            return True, session_data['username']
            
        except Exception as e:
            logger.error(f"Erro na validação de sessão: {e}")
            return False, None
    
    def logout(self, session_token: str) -> bool:
        """Encerra sessão."""
        try:
            if session_token in self.sessions:
                username = self.sessions[session_token]['username']
                del self.sessions[session_token]
                self._save_sessions()
                logger.info(f"Logout: {username}")
                return True
            return False
        except Exception as e:
            logger.error(f"Erro no logout: {e}")
            return False
    
    def change_password(self, username: str, old_password: str, 
                       new_password: str) -> bool:
        """Altera senha do usuário."""
        try:
            if username not in self.users:
                return False
            
            user = self.users[username]
            
            # Verifica senha atual
            if not self._verify_password(old_password, user['password_hash']):
                return False
            
            # Atualiza senha
            user['password_hash'] = self._hash_password(new_password)
            self._save_users()
            
            logger.info(f"Senha alterada: {username}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao alterar senha: {e}")
            return False
    
    def has_permission(self, username: str, permission: str) -> bool:
        """Verifica se usuário tem permissão específica."""
        try:
            if username not in self.users:
                return False
            
            user = self.users[username]
            permissions = user.get('permissions', [])
            
            return 'all' in permissions or permission in permissions
            
        except Exception as e:
            logger.error(f"Erro ao verificar permissão: {e}")
            return False
    
    def get_user_info(self, username: str) -> Optional[Dict]:
        """Retorna informações do usuário."""
        if username in self.users:
            user = self.users[username].copy()
            user.pop('password_hash', None)  # Remove hash da senha
            return user
        return None
    
    def list_active_sessions(self) -> List[Dict]:
        """Lista sessões ativas."""
        active_sessions = []
        
        for session_id, session_data in self.sessions.items():
            try:
                expires_at = datetime.fromisoformat(session_data['expires_at'])
                if expires_at > datetime.now():
                    session_info = session_data.copy()
                    session_info['session_id'] = session_id
                    active_sessions.append(session_info)
            except Exception:
                continue
        
        return active_sessions
    
    def generate_jwt_token(self, username: str, expires_in_hours: int = 24) -> str:
        """Gera token JWT."""
        try:
            payload = {
                'username': username,
                'exp': datetime.utcnow() + timedelta(hours=expires_in_hours),
                'iat': datetime.utcnow()
            }
            
            return jwt.encode(payload, self.jwt_secret, algorithm='HS256')
            
        except Exception as e:
            logger.error(f"Erro ao gerar JWT: {e}")
            return ""
    
    def validate_jwt_token(self, token: str) -> Tuple[bool, Optional[str]]:
        """Valida token JWT."""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            return True, payload.get('username')
            
        except jwt.ExpiredSignatureError:
            return False, None
        except jwt.InvalidTokenError:
            return False, None
        except Exception as e:
            logger.error(f"Erro ao validar JWT: {e}")
            return False, None


# Instância global do gerenciador de autenticação
auth_manager = AuthenticationManager()

# Decoradores para Flask
def require_auth(f):
    """Decorador que requer autenticação."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verifica header de autorização
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            valid, username = auth_manager.validate_jwt_token(token)
            if valid:
                request.current_user = username
                return f(*args, **kwargs)
        
        # Verifica sessão
        session_token = request.headers.get('X-Session-Token') or session.get('session_token')
        if session_token:
            valid, username = auth_manager.validate_session(session_token)
            if valid:
                request.current_user = username
                return f(*args, **kwargs)
        
        return jsonify({'error': 'Authentication required'}), 401
    
    return decorated_function

def require_permission(permission):
    """Decorador que requer permissão específica."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(request, 'current_user'):
                return jsonify({'error': 'Authentication required'}), 401
            
            if not auth_manager.has_permission(request.current_user, permission):
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def rate_limit(max_requests_per_minute=60):
    """Decorador para rate limiting."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.remote_addr
            if not auth_manager._check_rate_limit(client_ip):
                return jsonify({'error': 'Rate limit exceeded'}), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
