"""
Plugin de Segurança Avançado
Funções: detecção de ameaças, monitoramento de redes, verificação de segurança, análise de vulnerabilidades
"""

import os
import json
import hashlib
import psutil
import socket
import subprocess
import threading
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import logging
import re

logger = logging.getLogger(__name__)

class SecurityPlugin:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.security_log_file = "logs/security.log"
        self.threats_db_file = "data/threats.json"
        self.whitelist_file = "data/security_whitelist.json"
        self.monitoring_active = False
        self.monitoring_thread = None
        
        # Cria diretórios necessários
        os.makedirs("logs", exist_ok=True)
        os.makedirs("data", exist_ok=True)
        
        # Carrega dados de segurança
        self.known_threats = self._load_threats_db()
        self.whitelist = self._load_whitelist()
        
        # Configurações de monitoramento
        self.monitor_network = self.config.get('monitor_network', True)
        self.monitor_processes = self.config.get('monitor_processes', True)
        self.monitor_files = self.config.get('monitor_files', False)
        self.alert_threshold = self.config.get('alert_threshold', 80)
        
        logger.info("SecurityPlugin inicializado")

    def _load_threats_db(self) -> Dict[str, Any]:
        """Carrega base de dados de ameaças conhecidas."""
        try:
            if os.path.exists(self.threats_db_file):
                with open(self.threats_db_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Erro ao carregar DB de ameaças: {e}")
        
        # DB básico de ameaças
        return {
            "malicious_processes": [
                "virus.exe", "malware.exe", "trojan.exe", "keylogger.exe",
                "cryptominer.exe", "ransomware.exe"
            ],
            "suspicious_ports": [
                1234, 4444, 5555, 6666, 7777, 8888, 9999,
                12345, 31337, 54321
            ],
            "malicious_ips": [
                "192.168.1.100",  # Exemplo - substituir por IPs reais
            ],
            "file_extensions": [
                ".exe", ".scr", ".bat", ".cmd", ".com", ".pif", ".vbs", ".js"
            ]
        }

    def _load_whitelist(self) -> Dict[str, List[str]]:
        """Carrega lista branca de processos/IPs seguros."""
        try:
            if os.path.exists(self.whitelist_file):
                with open(self.whitelist_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Erro ao carregar whitelist: {e}")
        
        return {
            "safe_processes": [
                "system", "explorer.exe", "svchost.exe", "winlogon.exe",
                "python.exe", "code.exe", "chrome.exe", "firefox.exe"
            ],
            "safe_ips": [
                "127.0.0.1", "::1", "192.168.1.1"
            ]
        }

    def process(self, text: str) -> Optional[str]:
        """Processa comandos de segurança."""
        text_lower = text.lower().strip()
        
        # Comandos de monitoramento
        if any(word in text_lower for word in ['monitorar', 'monitor', 'vigilância']):
            if 'rede' in text_lower or 'network' in text_lower:
                return self._handle_network_monitoring(text)
            elif 'processo' in text_lower or 'process' in text_lower:
                return self._handle_process_monitoring(text)
            elif 'sistema' in text_lower or 'system' in text_lower:
                return self._handle_system_monitoring(text)
            else:
                return self._handle_general_monitoring(text)
        
        # Comandos de verificação
        elif any(word in text_lower for word in ['verificar', 'check', 'scan']):
            if 'vírus' in text_lower or 'virus' in text_lower or 'malware' in text_lower:
                return self._handle_malware_scan(text)
            elif 'porta' in text_lower or 'port' in text_lower:
                return self._handle_port_scan(text)
            elif 'segurança' in text_lower or 'security' in text_lower:
                return self._handle_security_check(text)
            else:
                return self._handle_general_check(text)
        
        # Comandos de análise
        elif any(word in text_lower for word in ['analisar', 'analyze', 'audit']):
            return self._handle_security_analysis(text)
        
        # Comandos de firewall
        elif any(word in text_lower for word in ['firewall', 'bloquer', 'block']):
            return self._handle_firewall_command(text)
        
        # Comandos de relatório
        elif any(word in text_lower for word in ['relatório', 'report', 'status']):
            return self._handle_security_report(text)
        
        return None

    def _handle_network_monitoring(self, text: str) -> str:
        """Gerencia monitoramento de rede."""
        if 'iniciar' in text.lower() or 'start' in text.lower():
            return self._start_network_monitoring()
        elif 'parar' in text.lower() or 'stop' in text.lower():
            return self._stop_monitoring()
        elif 'status' in text.lower():
            return self._get_monitoring_status()
        else:
            return self._get_network_info()

    def _handle_process_monitoring(self, text: str) -> str:
        """Gerencia monitoramento de processos."""
        return self._scan_processes()

    def _handle_system_monitoring(self, text: str) -> str:
        """Monitoramento geral do sistema."""
        return self._get_system_security_status()

    def _handle_general_monitoring(self, text: str) -> str:
        """Monitoramento geral."""
        if 'iniciar' in text.lower():
            return self._start_comprehensive_monitoring()
        else:
            return "🔒 Tipos de monitoramento: 'rede', 'processos', 'sistema'"

    def _handle_malware_scan(self, text: str) -> str:
        """Realiza varredura de malware."""
        return self._scan_for_malware()

    def _handle_port_scan(self, text: str) -> str:
        """Verifica portas abertas."""
        return self._scan_open_ports()

    def _handle_security_check(self, text: str) -> str:
        """Verificação geral de segurança."""
        return self._comprehensive_security_check()

    def _handle_general_check(self, text: str) -> str:
        """Verificação geral."""
        return "🔒 Tipos de verificação: 'malware', 'portas', 'segurança'"

    def _handle_security_analysis(self, text: str) -> str:
        """Análise de segurança."""
        return self._analyze_security_posture()

    def _handle_firewall_command(self, text: str) -> str:
        """Comandos de firewall."""
        return self._manage_firewall(text)

    def _handle_security_report(self, text: str) -> str:
        """Gera relatório de segurança."""
        return self._generate_security_report()

    def _start_network_monitoring(self) -> str:
        """Inicia monitoramento de rede."""
        if self.monitoring_active:
            return "🔒 Monitoramento já está ativo."
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitor_network_activity)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        self._log_security_event("Network monitoring started")
        return "🔒 Monitoramento de rede iniciado. Verificando conexões suspeitas..."

    def _stop_monitoring(self) -> str:
        """Para monitoramento."""
        if not self.monitoring_active:
            return "🔒 Monitoramento não está ativo."
        
        self.monitoring_active = False
        self._log_security_event("Monitoring stopped")
        return "🔒 Monitoramento interrompido."

    def _get_monitoring_status(self) -> str:
        """Retorna status do monitoramento."""
        if self.monitoring_active:
            return "🔒 Monitoramento ATIVO - Verificando ameaças em tempo real."
        else:
            return "🔒 Monitoramento INATIVO - Use 'monitorar rede' para iniciar."

    def _monitor_network_activity(self):
        """Thread de monitoramento de rede."""
        while self.monitoring_active:
            try:
                # Verifica conexões ativas
                connections = psutil.net_connections()
                suspicious_connections = []
                
                for conn in connections:
                    if conn.raddr:  # Tem endereço remoto
                        remote_ip = conn.raddr.ip
                        remote_port = conn.raddr.port
                        
                        # Verifica IP suspeito
                        if remote_ip in self.known_threats.get("malicious_ips", []):
                            suspicious_connections.append(f"IP malicioso: {remote_ip}:{remote_port}")
                        
                        # Verifica porta suspeita
                        if remote_port in self.known_threats.get("suspicious_ports", []):
                            suspicious_connections.append(f"Porta suspeita: {remote_ip}:{remote_port}")
                
                # Log atividades suspeitas
                for sus_conn in suspicious_connections:
                    self._log_security_event(f"Suspicious connection: {sus_conn}")
                
                time.sleep(5)  # Verifica a cada 5 segundos
                
            except Exception as e:
                logger.error(f"Erro no monitoramento de rede: {e}")
                time.sleep(10)

    def _get_network_info(self) -> str:
        """Retorna informações de rede."""
        try:
            # Estatísticas de rede
            net_io = psutil.net_io_counters()
            connections = len(psutil.net_connections())
            
            # Interfaces de rede
            interfaces = psutil.net_if_addrs()
            active_interfaces = len([i for i in interfaces.keys() if i != 'lo'])
            
            info = f"🌐 **Status da Rede:**\n"
            info += f"• Conexões ativas: {connections}\n"
            info += f"• Interfaces de rede: {active_interfaces}\n"
            info += f"• Bytes enviados: {net_io.bytes_sent:,}\n"
            info += f"• Bytes recebidos: {net_io.bytes_recv:,}\n"
            
            return info
            
        except Exception as e:
            return f"❌ Erro ao obter informações de rede: {e}"

    def _scan_processes(self) -> str:
        """Verifica processos suspeitos."""
        try:
            suspicious_processes = []
            high_cpu_processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    proc_info = proc.info
                    proc_name = proc_info['name'].lower()
                    
                    # Verifica processos maliciosos conhecidos
                    if proc_name in self.known_threats.get("malicious_processes", []):
                        suspicious_processes.append(f"{proc_info['name']} (PID: {proc_info['pid']})")
                    
                    # Verifica processos com alto uso de CPU
                    if proc_info['cpu_percent'] and proc_info['cpu_percent'] > self.alert_threshold:
                        high_cpu_processes.append(f"{proc_info['name']} ({proc_info['cpu_percent']:.1f}% CPU)")
                
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            result = "🔍 **Análise de Processos:**\n"
            
            if suspicious_processes:
                result += f"⚠️ Processos suspeitos encontrados:\n"
                for proc in suspicious_processes:
                    result += f"  • {proc}\n"
                    self._log_security_event(f"Suspicious process detected: {proc}")
            
            if high_cpu_processes:
                result += f"📊 Processos com alto uso de CPU:\n"
                for proc in high_cpu_processes:
                    result += f"  • {proc}\n"
            
            if not suspicious_processes and not high_cpu_processes:
                result += "✅ Nenhum processo suspeito detectado."
            
            return result
            
        except Exception as e:
            return f"❌ Erro na análise de processos: {e}"

    def _scan_for_malware(self) -> str:
        """Realiza varredura básica de malware."""
        try:
            threats_found = []
            
            # Verifica processos suspeitos
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    proc_name = proc.info['name'].lower()
                    if proc_name in self.known_threats.get("malicious_processes", []):
                        threats_found.append(f"Processo suspeito: {proc.info['name']}")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Verifica arquivos em locais suspeitos (implementação básica)
            suspicious_paths = [
                os.path.expanduser("~/Downloads"),
                os.path.expanduser("~/Desktop"),
                "C:\\Temp" if os.name == 'nt' else "/tmp"
            ]
            
            for path in suspicious_paths:
                if os.path.exists(path):
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            if any(file.lower().endswith(ext) for ext in self.known_threats.get("file_extensions", [])):
                                if any(threat in file.lower() for threat in self.known_threats.get("malicious_processes", [])):
                                    threats_found.append(f"Arquivo suspeito: {os.path.join(root, file)}")
            
            result = "🛡️ **Varredura de Malware:**\n"
            
            if threats_found:
                result += "⚠️ Ameaças detectadas:\n"
                for threat in threats_found:
                    result += f"  • {threat}\n"
                    self._log_security_event(f"Malware detected: {threat}")
                result += "\n⚠️ Recomendação: Execute um antivírus completo."
            else:
                result += "✅ Nenhuma ameaça detectada na varredura básica."
            
            return result
            
        except Exception as e:
            return f"❌ Erro na varredura: {e}"

    def _scan_open_ports(self) -> str:
        """Verifica portas abertas."""
        try:
            open_ports = []
            suspicious_ports = []
            
            # Verifica portas em uso
            connections = psutil.net_connections()
            
            for conn in connections:
                if conn.status == 'LISTEN':
                    port = conn.laddr.port
                    open_ports.append(port)
                    
                    if port in self.known_threats.get("suspicious_ports", []):
                        suspicious_ports.append(port)
            
            result = "🔌 **Análise de Portas:**\n"
            result += f"• Portas abertas: {len(set(open_ports))}\n"
            
            if suspicious_ports:
                result += f"⚠️ Portas suspeitas abertas:\n"
                for port in set(suspicious_ports):
                    result += f"  • Porta {port}\n"
                    self._log_security_event(f"Suspicious port open: {port}")
            
            # Mostra algumas portas abertas comuns
            common_ports = [port for port in set(open_ports) if port in [80, 443, 22, 21, 25, 53, 110, 143, 993, 995]]
            if common_ports:
                result += f"• Portas comuns abertas: {', '.join(map(str, common_ports))}\n"
            
            return result
            
        except Exception as e:
            return f"❌ Erro na análise de portas: {e}"

    def _get_system_security_status(self) -> str:
        """Retorna status geral de segurança do sistema."""
        try:
            # CPU e memória
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # Processos
            process_count = len(psutil.pids())
            
            # Uptime
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            
            status = "🖥️ **Status de Segurança do Sistema:**\n"
            status += f"• CPU: {cpu_percent}%\n"
            status += f"• Memória: {memory.percent}%\n"
            status += f"• Processos ativos: {process_count}\n"
            status += f"• Uptime: {uptime.days} dias, {uptime.seconds//3600} horas\n"
            
            # Alertas
            if cpu_percent > 90:
                status += "⚠️ Alto uso de CPU detectado!\n"
            if memory.percent > 90:
                status += "⚠️ Alto uso de memória detectado!\n"
            
            return status
            
        except Exception as e:
            return f"❌ Erro ao obter status: {e}"

    def _comprehensive_security_check(self) -> str:
        """Verificação completa de segurança."""
        try:
            results = []
            
            # Verifica processos
            proc_result = self._scan_processes()
            if "suspeitos encontrados" in proc_result:
                results.append("⚠️ Processos suspeitos detectados")
            else:
                results.append("✅ Processos verificados")
            
            # Verifica portas
            port_result = self._scan_open_ports()
            if "suspeitas abertas" in port_result:
                results.append("⚠️ Portas suspeitas abertas")
            else:
                results.append("✅ Portas verificadas")
            
            # Verifica sistema
            system_result = self._get_system_security_status()
            if "Alto uso" in system_result:
                results.append("⚠️ Recursos do sistema sob pressão")
            else:
                results.append("✅ Sistema estável")
            
            summary = "🔒 **Verificação Completa de Segurança:**\n"
            summary += "\n".join(results)
            
            return summary
            
        except Exception as e:
            return f"❌ Erro na verificação: {e}"

    def _log_security_event(self, event: str):
        """Registra evento de segurança."""
        try:
            timestamp = datetime.now().isoformat()
            log_entry = f"[{timestamp}] {event}\n"
            
            with open(self.security_log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
                
        except Exception as e:
            logger.error(f"Erro ao registrar evento: {e}")

    def _generate_security_report(self) -> str:
        """Gera relatório de segurança."""
        try:
            report = "📋 **Relatório de Segurança - " + datetime.now().strftime("%d/%m/%Y %H:%M") + "**\n\n"
            
            # Status do monitoramento
            if self.monitoring_active:
                report += "🔒 Monitoramento: ATIVO\n"
            else:
                report += "🔒 Monitoramento: INATIVO\n"
            
            # Últimos eventos de segurança
            try:
                if os.path.exists(self.security_log_file):
                    with open(self.security_log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        recent_events = lines[-5:]  # Últimos 5 eventos
                        
                    if recent_events:
                        report += "\n📊 Eventos Recentes:\n"
                        for event in recent_events:
                            report += f"  • {event.strip()}\n"
                    else:
                        report += "\n📊 Nenhum evento recente registrado.\n"
            except Exception as e:
                report += f"\n❌ Erro ao ler log de eventos: {e}\n"
            
            # Resumo rápido do sistema
            report += f"\n{self._get_system_security_status()}"
            
            return report
            
        except Exception as e:
            return f"❌ Erro ao gerar relatório: {e}"

    def _analyze_security_posture(self) -> str:
        """Análise da postura de segurança."""
        analysis = "🔍 **Análise de Postura de Segurança:**\n\n"
        
        # Pontuação de segurança
        score = 100
        issues = []
        
        # Verifica se o monitoramento está ativo
        if not self.monitoring_active:
            score -= 20
            issues.append("Monitoramento não está ativo")
        
        # Verifica uso de recursos
        try:
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            
            if cpu_percent > 80:
                score -= 10
                issues.append("Alto uso de CPU")
            
            if memory_percent > 80:
                score -= 10
                issues.append("Alto uso de memória")
                
        except Exception:
            pass
        
        # Verifica se há logs de segurança
        if not os.path.exists(self.security_log_file):
            score -= 5
            issues.append("Nenhum log de segurança encontrado")
        
        # Resultado da análise
        if score >= 90:
            analysis += "✅ **Postura de Segurança: EXCELENTE**\n"
        elif score >= 70:
            analysis += "🟡 **Postura de Segurança: BOA**\n"
        elif score >= 50:
            analysis += "🟠 **Postura de Segurança: REGULAR**\n"
        else:
            analysis += "🔴 **Postura de Segurança: CRÍTICA**\n"
        
        analysis += f"Pontuação: {score}/100\n\n"
        
        if issues:
            analysis += "⚠️ **Problemas Identificados:**\n"
            for issue in issues:
                analysis += f"  • {issue}\n"
        else:
            analysis += "✅ Nenhum problema crítico identificado.\n"
        
        return analysis

    def _manage_firewall(self, text: str) -> str:
        """Gerencia configurações de firewall."""
        return "🔥 Gerenciamento de firewall requer privilégios de administrador. Funcionalidade em desenvolvimento."

    def _start_comprehensive_monitoring(self) -> str:
        """Inicia monitoramento abrangente."""
        self.monitoring_active = True
        
        # Inicia múltiplos tipos de monitoramento
        self.monitoring_thread = threading.Thread(target=self._comprehensive_monitoring)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        return "🔒 Monitoramento abrangente iniciado (rede, processos, sistema)."

    def _comprehensive_monitoring(self):
        """Thread de monitoramento abrangente."""
        while self.monitoring_active:
            try:
                # Monitoramento de rede
                self._monitor_network_activity()
                
                # Verifica processos suspeitos
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        if proc.info['name'].lower() in self.known_threats.get("malicious_processes", []):
                            self._log_security_event(f"Suspicious process detected: {proc.info['name']}")
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                time.sleep(30)  # Verifica a cada 30 segundos
                
            except Exception as e:
                logger.error(f"Erro no monitoramento abrangente: {e}")
                time.sleep(60)

    def detect_threats(self, data: Any) -> str:
        """Detecta ameaças em dados fornecidos."""
        try:
            threats = []
            
            if isinstance(data, str):
                # Análise de texto/log
                if any(threat in data.lower() for threat in self.known_threats.get("malicious_processes", [])):
                    threats.append("Processo malicioso mencionado")
                
                # Verifica padrões suspeitos
                if re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', data):
                    threats.append("Endereço IP detectado")
            
            if threats:
                return f"⚠️ Ameaças detectadas: {', '.join(threats)}"
            else:
                return "✅ Nenhuma ameaça detectada nos dados fornecidos."
                
        except Exception as e:
            return f"❌ Erro na detecção: {e}"

    def monitor_network(self, network_data: Any = None) -> str:
        """Monitora atividade de rede."""
        if network_data:
            return self.detect_threats(network_data)
        else:
            return self._get_network_info()
