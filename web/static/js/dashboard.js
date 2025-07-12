// JARVIS 3.0 - Dashboard JavaScript

class JarvisDashboard {
    constructor() {
        this.socket = io();
        this.charts = {};
        this.isMonitoring = false;
        this.systemData = [];
        
        // CORREÇÃO: Limpeza automática periódica para garantir que gráficos não cresçam
        this.cleanupInterval = setInterval(() => {
            this.forceCleanupCharts();
        }, 30000); // Limpa a cada 30 segundos
        
        this.init();
    }
    
    init() {
        this.setupSocketEvents();
        this.setupEventListeners();
        this.initializeCharts();
        this.loadInitialData();
    }
    
    setupSocketEvents() {
        this.socket.on('connect', () => {
            console.log('🔗 Conectado ao servidor');
            this.updateConnectionStatus('🟢 Conectado');
        });
        
        this.socket.on('disconnect', () => {
            console.log('❌ Desconectado do servidor');
            this.updateConnectionStatus('🔴 Desconectado');
        });
        
        this.socket.on('system_update', (data) => {
            this.updateSystemData(data);
        });
        
        this.socket.on('monitoring_started', () => {
            this.isMonitoring = true;
            this.updateMonitoringControls();
        });
        
        this.socket.on('monitoring_stopped', () => {
            this.isMonitoring = false;
            this.updateMonitoringControls();
        });
    }
    
    setupEventListeners() {
        // Controles de monitoramento
        document.getElementById('start-monitoring')?.addEventListener('click', () => {
            this.startMonitoring();
        });
        
        document.getElementById('stop-monitoring')?.addEventListener('click', () => {
            this.stopMonitoring();
        });
        
        // Atualização manual
        document.addEventListener('keydown', (e) => {
            if (e.key === 'F5' || (e.ctrlKey && e.key === 'r')) {
                e.preventDefault();
                this.refreshData();
            }
        });
    }
    
    async loadInitialData() {
        try {
            const response = await fetch('/api/system/info');
            const data = await response.json();
            
            if (data.success) {
                this.updateSystemData({ ...data.data, timestamp: Date.now() / 1000 });
            }
        } catch (error) {
            console.error('Erro ao carregar dados iniciais:', error);
        }
    }
    
    updateSystemData(data) {
        // Valida dados antes de processar
        if (!data || typeof data !== 'object') {
            console.warn('Dados de sistema inválidos recebidos');
            return;
        }
        
        // Atualiza cards de status
        this.updateStatusCards(data);
        
        // Só atualiza gráficos se monitoramento estiver ativo
        if (this.isMonitoring) {
            this.updateCharts(data);
        }
        
        // Atualiza status bar
        this.updateStatusBar(data);
        
        // CORREÇÃO CRÍTICA: Limita histórico rigorosamente a 15 pontos (máximo absoluto)
        const maxHistoryPoints = 15;
        this.systemData.push(data);
        
        // Remove pontos antigos em lote se ultrapassar o limite
        if (this.systemData.length > maxHistoryPoints) {
            this.systemData = this.systemData.slice(-maxHistoryPoints);
        }
    }
    
    updateStatusCards(data) {
        // CPU
        this.updateCard('cpu', {
            percent: data.cpu_percent,
            status: this.getStatusLevel(data.cpu_percent, 70, 90)
        });
        
        // Memória
        this.updateCard('memory', {
            percent: data.memory_percent,
            used: data.memory_used,
            total: data.memory_total,
            status: this.getStatusLevel(data.memory_percent, 70, 85)
        });
        
        // Disco
        this.updateCard('disk', {
            percent: data.disk_percent,
            used: data.disk_used,
            total: data.disk_total,
            status: this.getStatusLevel(data.disk_percent, 80, 90)
        });
        
        // Bateria
        if (data.battery_percent !== null) {
            this.updateCard('battery', {
                percent: data.battery_percent,
                plugged: data.battery_plugged,
                status: this.getBatteryStatus(data.battery_percent, data.battery_plugged)
            });
        }
        
        // Rede
        this.updateNetworkStats(data.network_sent, data.network_recv);
        
        // Temperatura
        if (data.temperature !== null) {
            this.updateTemperature(data.temperature);
        }
    }
    
    updateCard(type, data) {
        const percentElement = document.getElementById(`${type}-percent`);
        const progressElement = document.getElementById(`${type}-progress`);
        const statusElement = document.getElementById(`${type}-status`);
        const detailsElement = document.getElementById(`${type}-details`);
        
        if (percentElement) {
            percentElement.textContent = `${Math.round(data.percent)}%`;
        }
        
        if (progressElement) {
            progressElement.style.width = `${data.percent}%`;
        }
        
        if (statusElement) {
            statusElement.className = `status-indicator ${data.status}`;
        }
        
        if (detailsElement && data.used && data.total) {
            detailsElement.textContent = `${data.used.toFixed(1)} GB / ${data.total.toFixed(1)} GB`;
        }
        
        // Caso especial para bateria
        if (type === 'battery' && detailsElement) {
            const status = data.plugged ? '🔌 Conectado' : '🔋 Bateria';
            detailsElement.textContent = status;
        }
    }
    
    updateNetworkStats(sent, recv) {
        const sentElement = document.getElementById('network-sent');
        const recvElement = document.getElementById('network-recv');
        
        if (sentElement) {
            sentElement.textContent = `${sent.toFixed(2)} MB/s`;
        }
        
        if (recvElement) {
            recvElement.textContent = `${recv.toFixed(2)} MB/s`;
        }
    }
    
    updateTemperature(temp) {
        const tempElement = document.getElementById('temp-value');
        if (tempElement) {
            tempElement.textContent = `${Math.round(temp)}°C`;
            
            // Muda cor baseado na temperatura
            if (temp > 80) {
                tempElement.style.color = '#ff4444';
            } else if (temp > 60) {
                tempElement.style.color = '#ffaa00';
            } else {
                tempElement.style.color = '#00ff88';
            }
        }
    }
    
    getStatusLevel(value, warning, danger) {
        if (value >= danger) return 'danger';
        if (value >= warning) return 'warning';
        return 'success';
    }
    
    getBatteryStatus(percent, plugged) {
        if (plugged) return 'success';
        if (percent <= 20) return 'danger';
        if (percent <= 50) return 'warning';
        return 'success';
    }
    
    initializeCharts() {
        this.initPerformanceChart();
        this.initTemperatureChart();
        this.initNetworkChart();
    }
    
    initPerformanceChart() {
        const ctx = document.getElementById('performance-chart');
        if (!ctx) return;
        
        this.charts.performance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'CPU %',
                        data: [],
                        borderColor: '#00d4ff',
                        backgroundColor: 'rgba(0, 212, 255, 0.1)',
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: 'Memória %',
                        data: [],
                        borderColor: '#00ff88',
                        backgroundColor: 'rgba(0, 255, 136, 0.1)',
                        tension: 0.4,
                        fill: true
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: '#ffffff'
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: { color: '#b0b0b0' },
                        grid: { color: '#333333' }
                    },
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { color: '#b0b0b0' },
                        grid: { color: '#333333' }
                    }
                },
                animation: {
                    duration: 750
                }
            }
        });
    }
    
    initTemperatureChart() {
        const ctx = document.getElementById('temperature-chart');
        if (!ctx) return;
        
        this.charts.temperature = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Usado', 'Disponível'],
                datasets: [{
                    data: [0, 100],
                    backgroundColor: ['#ff4444', '#333333'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                cutout: '70%'
            }
        });
    }
    
    initNetworkChart() {
        const ctx = document.getElementById('network-chart');
        if (!ctx) return;
        
        this.charts.network = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Upload (MB/s)',
                        data: [],
                        backgroundColor: '#00d4ff',
                        borderRadius: 4
                    },
                    {
                        label: 'Download (MB/s)',
                        data: [],
                        backgroundColor: '#00ff88',
                        borderRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#ffffff' }
                    }
                },
                scales: {
                    x: {
                        ticks: { color: '#b0b0b0' },
                        grid: { color: '#333333' }
                    },
                    y: {
                        beginAtZero: true,
                        ticks: { color: '#b0b0b0' },
                        grid: { color: '#333333' }
                    }
                }
            }
        });
    }
    
    updateCharts(data) {
        // Só atualiza gráficos se monitoramento estiver ativo
        if (!this.isMonitoring) return;
        
        const timestamp = new Date(data.timestamp * 1000).toLocaleTimeString();
        
        // Performance Chart - LIMITE RIGOROSO DE 20 PONTOS (máximo absoluto)
        if (this.charts.performance) {
            const chart = this.charts.performance;
            const maxPoints = 20;
            
            // SEMPRE remove pontos antigos ANTES de adicionar novos
            if (chart.data.labels.length >= maxPoints) {
                // Remove múltiplos pontos se necessário
                const pointsToRemove = chart.data.labels.length - maxPoints + 1;
                for (let i = 0; i < pointsToRemove; i++) {
                    chart.data.labels.shift();
                    chart.data.datasets[0].data.shift();
                    chart.data.datasets[1].data.shift();
                }
            }
            
            // Adiciona novos dados (arredondados para reduzir noise)
            chart.data.labels.push(timestamp);
            chart.data.datasets[0].data.push(Math.round(data.cpu_percent * 10) / 10);
            chart.data.datasets[1].data.push(Math.round(data.memory_percent * 10) / 10);
            
            // Update sem animação para melhor performance
            chart.update('none');
        }
        
        // Temperature Chart - Atualização simples
        if (this.charts.temperature && data.temperature !== null && data.temperature !== undefined) {
            const tempPercent = Math.min(Math.max(data.temperature, 0), 100);
            this.charts.temperature.data.datasets[0].data = [tempPercent, 100 - tempPercent];
            this.charts.temperature.update('none');
        }
        
        // Network Chart - LIMITE RIGOROSO DE 10 PONTOS (máximo absoluto)
        if (this.charts.network) {
            const chart = this.charts.network;
            const maxPoints = 10;
            
            // SEMPRE remove pontos antigos ANTES de adicionar novos
            if (chart.data.labels.length >= maxPoints) {
                const pointsToRemove = chart.data.labels.length - maxPoints + 1;
                for (let i = 0; i < pointsToRemove; i++) {
                    chart.data.labels.shift();
                    chart.data.datasets[0].data.shift();
                    chart.data.datasets[1].data.shift();
                }
            }
            
            // Adiciona dados de rede (limitados e arredondados)
            chart.data.labels.push(timestamp);
            chart.data.datasets[0].data.push(Math.round((Math.min(data.network_sent || 0, 100)) * 100) / 100);
            chart.data.datasets[1].data.push(Math.round((Math.min(data.network_recv || 0, 100)) * 100) / 100);
            
            chart.update('none');
        }
    }
    
    forceCleanupCharts() {
        /**
         * CORREÇÃO CRÍTICA: Limpeza forçada para evitar crescimento infinito dos gráficos
         * Esta função é executada periodicamente para garantir que os gráficos
         * nunca ultrapassem os limites estabelecidos
         */
        
        // Performance Chart - Limita a 15 pontos máximo
        if (this.charts.performance) {
            const chart = this.charts.performance;
            const maxPoints = 15;
            
            if (chart.data.labels.length > maxPoints) {
                chart.data.labels = chart.data.labels.slice(-maxPoints);
                chart.data.datasets[0].data = chart.data.datasets[0].data.slice(-maxPoints);
                chart.data.datasets[1].data = chart.data.datasets[1].data.slice(-maxPoints);
                chart.update('none');
            }
        }
        
        // Network Chart - Limita a 8 pontos máximo
        if (this.charts.network) {
            const chart = this.charts.network;
            const maxPoints = 8;
            
            if (chart.data.labels.length > maxPoints) {
                chart.data.labels = chart.data.labels.slice(-maxPoints);
                chart.data.datasets[0].data = chart.data.datasets[0].data.slice(-maxPoints);
                chart.data.datasets[1].data = chart.data.datasets[1].data.slice(-maxPoints);
                chart.update('none');
            }
        }
        
        // Limpa histórico de dados também
        const maxHistoryPoints = 10;
        if (this.systemData.length > maxHistoryPoints) {
            this.systemData = this.systemData.slice(-maxHistoryPoints);
        }
        
        console.log('🧹 Limpeza automática dos gráficos executada');
    }
    
    updateStatusBar(data) {
        const lastUpdateElement = document.getElementById('last-update');
        const uptimeElement = document.getElementById('uptime');
        
        if (lastUpdateElement) {
            lastUpdateElement.textContent = `Última atualização: ${new Date().toLocaleTimeString()}`;
        }
        
        if (uptimeElement && data.uptime) {
            const hours = Math.floor(data.uptime);
            const minutes = Math.floor((data.uptime - hours) * 60);
            uptimeElement.textContent = `Uptime: ${hours}h ${minutes}m`;
        }
    }
    
    updateConnectionStatus(status) {
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            statusElement.textContent = status;
        }
    }
    
    updateMonitoringControls() {
        this.updateMonitoringButtons();
        this.updateVisualIndicators();
    }
    
    updateMonitoringButtons() {
        const startBtn = document.getElementById('start-monitoring');
        const stopBtn = document.getElementById('stop-monitoring');
        
        if (startBtn) {
            startBtn.disabled = this.isMonitoring;
            startBtn.style.opacity = this.isMonitoring ? '0.5' : '1';
            startBtn.textContent = this.isMonitoring ? '✅ Monitoramento Ativo' : '▶️ Iniciar Monitoramento';
        }
        
        if (stopBtn) {
            stopBtn.disabled = !this.isMonitoring;
            stopBtn.style.opacity = !this.isMonitoring ? '0.5' : '1';
            stopBtn.textContent = !this.isMonitoring ? '⏹️ Parado' : '⏹️ Parar Monitoramento';
        }
    }
    
    updateVisualIndicators() {
        // CORREÇÃO: Atualiza indicador visual de status do monitoramento
        const performanceSection = document.querySelector('.chart-container');
        if (performanceSection) {
            if (this.isMonitoring) {
                performanceSection.style.border = '2px solid #00ff88';
                performanceSection.style.boxShadow = '0 0 20px rgba(0, 255, 136, 0.4)';
                performanceSection.style.backgroundColor = 'rgba(0, 255, 136, 0.02)';
            } else {
                performanceSection.style.border = '2px solid #333';
                performanceSection.style.boxShadow = 'none';
                performanceSection.style.backgroundColor = 'transparent';
            }
        }
        
        // Adiciona indicador no título da seção
        const performanceTitle = document.querySelector('.chart-container h3');
        if (performanceTitle) {
            const statusText = this.isMonitoring ? ' (🟢 ATIVO)' : ' (🔴 PARADO)';
            const cleanTitle = performanceTitle.textContent.replace(/ \(.*\)/, '');
            performanceTitle.textContent = cleanTitle + statusText;
        }
    }
    
    startMonitoring() {
        this.socket.emit('start_monitoring');
    }
    
    stopMonitoring() {
        this.socket.emit('stop_monitoring');
    }
    
    async refreshData() {
        try {
            const response = await fetch('/api/system/info');
            const data = await response.json();
            
            if (data.success) {
                this.updateSystemData({ ...data.data, timestamp: Date.now() / 1000 });
                this.showNotification('✅ Dados atualizados com sucesso!');
            }
        } catch (error) {
            console.error('Erro ao atualizar dados:', error);
            this.showNotification('❌ Erro ao atualizar dados');
        }
    }
    
    showNotification(message) {
        // Cria notificação temporária
        const notification = document.createElement('div');
        notification.className = 'notification';
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--accent-primary);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            z-index: 1000;
            animation: slideIn 0.3s ease-out;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
    
    destroy() {
        /**
         * CORREÇÃO: Método para limpar recursos quando a instância não for mais necessária
         */
        if (this.cleanupInterval) {
            clearInterval(this.cleanupInterval);
        }
        
        // Para monitoramento se estiver ativo
        if (this.isMonitoring) {
            this.stopMonitoring();
        }
        
        console.log('🗑️ Dashboard destruído e recursos limpos');
    }
}

// Funções globais para ações rápidas
function openChat() {
    window.location.href = '/chat';
}

function refreshData() {
    if (window.dashboard) {
        window.dashboard.refreshData();
    }
}

function exportData() {
    // Implementar exportação de dados
    alert('Funcionalidade de exportação em desenvolvimento');
}

function openSettings() {
    // Implementar configurações
    alert('Configurações em desenvolvimento');
}

// Inicializa dashboard quando a página carrega
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new JarvisDashboard();
});

// Adiciona estilo para notificações
const style = document.createElement('style');
style.textContent = `
@keyframes slideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}
`;
document.head.appendChild(style);
