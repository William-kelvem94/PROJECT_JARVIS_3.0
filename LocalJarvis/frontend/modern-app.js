// 🚀 JARVIS 3.0 - Modern JavaScript Interface

class JarvisModernInterface {
    constructor() {
        this.currentModule = 'assistant';
        this.isLoading = true;
        this.chatMessages = [];
        this.plugins = [];
        this.metrics = {
            cpu: 0,
            ram: 0,
            disk: 0,
            plugins: 0
        };
        this.isVoiceActive = false;
        this.quickActionsOpen = false;
        
        this.init();
    }

    async init() {
        console.log('🤖 Initializing JARVIS 3.0 Modern Interface...');
        
        // Show loading screen
        this.showLoadingScreen();
        
        // Initialize components
        await this.initializeComponents();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Load initial data
        await this.loadInitialData();
        
        // Hide loading screen and show app
        this.hideLoadingScreen();
        
        // Start real-time updates
        this.startRealTimeUpdates();
        
        console.log('✅ JARVIS 3.0 Ready!');
    }

    showLoadingScreen() {
        const loadingScreen = document.getElementById('loadingScreen');
        const statusElement = document.getElementById('loadingStatus');
        
        const loadingSteps = [
            'Inicializando núcleo do sistema...',
            'Carregando módulos de IA...',
            'Conectando aos serviços...',
            'Configurando interface...',
            'Ativando protocolos de segurança...',
            'Sistema pronto!'
        ];
        
        let step = 0;
        const loadingInterval = setInterval(() => {
            if (step < loadingSteps.length) {
                statusElement.textContent = loadingSteps[step];
                step++;
            } else {
                clearInterval(loadingInterval);
            }
        }, 500);
    }

    hideLoadingScreen() {
        setTimeout(() => {
            const loadingScreen = document.getElementById('loadingScreen');
            const mainApp = document.getElementById('mainApp');
            
            loadingScreen.classList.add('hidden');
            mainApp.classList.remove('hidden');
            
            // Add entrance animation
            mainApp.style.animation = 'fadeIn 1s ease-out';
        }, 3000);
    }

    async initializeComponents() {
        // Initialize system time
        this.updateSystemTime();
        setInterval(() => this.updateSystemTime(), 1000);
        
        // Initialize chat with welcome message
        this.initializeChat();
        
        // Initialize modules
        this.initializeModules();
    }

    updateSystemTime() {
        const timeElement = document.getElementById('systemTime');
        if (timeElement) {
            const now = new Date();
            const timeString = now.toLocaleTimeString('pt-BR', { 
                hour12: false,
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
            timeElement.textContent = timeString;
        }
    }

    initializeChat() {
        const initTimeElement = document.getElementById('initTime');
        if (initTimeElement) {
            initTimeElement.textContent = new Date().toLocaleTimeString('pt-BR');
        }
    }

    initializeModules() {
        // Set up module navigation
        const moduleButtons = document.querySelectorAll('.module-btn');
        moduleButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const module = btn.dataset.module;
                this.switchModule(module);
            });
        });
    }

    setupEventListeners() {
        // Chat input
        const chatInput = document.getElementById('chatInput');
        const sendBtn = document.getElementById('sendBtn');
        const voiceBtn = document.getElementById('voiceBtn');

        if (chatInput) {
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.sendMessage();
                }
            });
        }

        if (sendBtn) {
            sendBtn.addEventListener('click', () => this.sendMessage());
        }

        if (voiceBtn) {
            voiceBtn.addEventListener('click', () => this.toggleVoice());
        }

        // Module controls
        this.setupModuleControls();
    }

    setupModuleControls() {
        // Vision controls
        const cameraBtn = document.querySelector('[onclick="startCamera()"]');
        if (cameraBtn) {
            cameraBtn.onclick = () => this.startCamera();
        }

        const captureBtn = document.querySelector('[onclick="captureImage()"]');
        if (captureBtn) {
            captureBtn.onclick = () => this.captureImage();
        }

        const uploadBtn = document.querySelector('[onclick="uploadImage()"]');
        if (uploadBtn) {
            uploadBtn.onclick = () => this.uploadImage();
        }

        // Training controls
        const uploadZone = document.querySelector('[onclick="uploadTrainingData()"]');
        if (uploadZone) {
            uploadZone.onclick = () => this.uploadTrainingData();
        }

        // Plugin controls
        const refreshBtn = document.querySelector('[onclick="refreshPlugins()"]');
        if (refreshBtn) {
            refreshBtn.onclick = () => this.refreshPlugins();
        }
    }

    switchModule(moduleName) {
        // Update navigation
        document.querySelectorAll('.module-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-module="${moduleName}"]`).classList.add('active');

        // Update content
        document.querySelectorAll('.module-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${moduleName}-module`).classList.add('active');

        this.currentModule = moduleName;
        
        // Load module-specific data
        this.loadModuleData(moduleName);
    }

    async loadModuleData(moduleName) {
        switch(moduleName) {
            case 'vision':
                await this.loadVisionData();
                break;
            case 'security':
                await this.loadSecurityData();
                break;
            case 'plugins':
                await this.loadPluginsData();
                break;
            case 'training':
                await this.loadTrainingData();
                break;
            case 'analytics':
                await this.loadAnalyticsData();
                break;
        }
    }

    async loadInitialData() {
        try {
            // Load metrics
            await this.updateMetrics();
            
            // Load plugins
            await this.loadPluginsData();
            
        } catch (error) {
            console.error('Error loading initial data:', error);
        }
    }

    async sendMessage() {
        const input = document.getElementById('chatInput');
        const message = input.value.trim();
        
        if (!message) return;

        // Add user message to chat
        this.addChatMessage('user', message);
        input.value = '';

        // Show typing indicator
        this.showTypingIndicator();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    message: message,
                    module: this.currentModule,
                    timestamp: new Date().toISOString()
                })
            });

            const data = await response.json();
            
            this.hideTypingIndicator();
            
            if (data.response) {
                this.addChatMessage('assistant', data.response);
            }
            
            // Handle any actions
            if (data.actions) {
                this.executeActions(data.actions);
            }
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.hideTypingIndicator();
            this.addChatMessage('assistant', '❌ Erro de conexão. Tente novamente.');
        }
    }

    addChatMessage(sender, message) {
        const messagesContainer = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `${sender}-message`;
        
        const time = new Date().toLocaleTimeString('pt-BR');
        const senderName = sender === 'user' ? 'USUÁRIO' : 'JARVIS 3.0';
        
        messageDiv.innerHTML = `
            <div class="message-icon">
                <i class="fas fa-${sender === 'user' ? 'user' : 'robot'}"></i>
            </div>
            <div class="message-content">
                <div class="message-header">
                    <span class="sender-name">${senderName}</span>
                    <span class="message-time">${time}</span>
                </div>
                <div class="message-text">${this.formatMessage(message)}</div>
            </div>
        `;
        
        messagesContainer.appendChild(messageDiv);
        this.scrollChatToBottom();
        
        // Store message
        this.chatMessages.push({ sender, message, time });
    }

    formatMessage(message) {
        return message
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>');
    }

    showTypingIndicator() {
        const messagesContainer = document.getElementById('chatMessages');
        const typingDiv = document.createElement('div');
        typingDiv.className = 'assistant-message typing-indicator';
        typingDiv.id = 'typingIndicator';
        
        typingDiv.innerHTML = `
            <div class="message-icon">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <div class="message-header">
                    <span class="sender-name">JARVIS 3.0</span>
                    <span class="message-time">${new Date().toLocaleTimeString('pt-BR')}</span>
                </div>
                <div class="message-text">
                    <div class="typing-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                    Processando...
                </div>
            </div>
        `;
        
        messagesContainer.appendChild(typingDiv);
        this.scrollChatToBottom();
    }

    hideTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) {
            indicator.remove();
        }
    }

    scrollChatToBottom() {
        const messagesContainer = document.getElementById('chatMessages');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    async toggleVoice() {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            this.showNotification('Erro', 'Reconhecimento de voz não suportado', 'error');
            return;
        }

        if (this.isVoiceActive) {
            this.stopVoiceRecognition();
        } else {
            this.startVoiceRecognition();
        }
    }

    startVoiceRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();
        
        this.recognition.continuous = false;
        this.recognition.interimResults = false;
        this.recognition.lang = 'pt-BR';

        this.recognition.onstart = () => {
            this.isVoiceActive = true;
            const voiceBtn = document.getElementById('voiceBtn');
            voiceBtn.style.background = 'linear-gradient(135deg, #ff0080, #00ffff)';
            voiceBtn.style.animation = 'pulse 1s infinite';
            this.showNotification('🎤', 'Escutando...', 'info');
        };

        this.recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            const chatInput = document.getElementById('chatInput');
            chatInput.value = transcript;
            this.sendMessage();
        };

        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            this.showNotification('❌', 'Erro no reconhecimento de voz', 'error');
        };

        this.recognition.onend = () => {
            this.isVoiceActive = false;
            const voiceBtn = document.getElementById('voiceBtn');
            voiceBtn.style.background = '';
            voiceBtn.style.animation = '';
        };

        this.recognition.start();
    }

    stopVoiceRecognition() {
        if (this.recognition) {
            this.recognition.stop();
        }
    }

    // Vision Module Methods
    async startCamera() {
        try {
            const video = document.getElementById('cameraFeed');
            const stream = await navigator.mediaDevices.getUserMedia({ 
                video: { width: 640, height: 480 } 
            });
            
            video.srcObject = stream;
            this.showNotification('📹', 'Câmera ativada', 'success');
        } catch (error) {
            console.error('Camera error:', error);
            this.showNotification('❌', 'Erro ao acessar câmera', 'error');
        }
    }

    captureImage() {
        const video = document.getElementById('cameraFeed');
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0);
        
        canvas.toBlob(blob => {
            this.analyzeImage(blob);
        }, 'image/jpeg', 0.8);
    }

    uploadImage() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/*';
        
        input.onchange = (e) => {
            const file = e.target.files[0];
            if (file) {
                this.analyzeImage(file);
            }
        };
        
        input.click();
    }

    async analyzeImage(imageData) {
        const formData = new FormData();
        formData.append('image', imageData);
        
        try {
            const response = await fetch('/api/vision/analyze', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            this.displayVisionResults(result);
            
        } catch (error) {
            console.error('Image analysis error:', error);
            this.showNotification('❌', 'Erro na análise da imagem', 'error');
        }
    }

    displayVisionResults(results) {
        const resultsContainer = document.getElementById('visionResults');
        
        if (results.objects && results.objects.length > 0) {
            resultsContainer.innerHTML = `
                <div class="vision-result">
                    <h4>🎯 Objetos Detectados</h4>
                    <div class="detected-objects">
                        ${results.objects.map(obj => `
                            <div class="object-item">
                                <span class="object-name">${obj.name}</span>
                                <span class="object-confidence">${(obj.confidence * 100).toFixed(1)}%</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        } else {
            resultsContainer.innerHTML = `
                <div class="no-results">
                    <i class="fas fa-search-plus"></i>
                    <p>Nenhum objeto detectado</p>
                </div>
            `;
        }
    }

    // Security Module Methods
    async loadSecurityData() {
        try {
            const response = await fetch('/api/security/metrics');
            const data = await response.json();
            
            // Update security metrics display
            this.updateSecurityDisplay(data);
            
        } catch (error) {
            console.error('Security data error:', error);
        }
    }

    updateSecurityDisplay(data) {
        // Update security level
        const levelElement = document.querySelector('.security-level');
        if (levelElement && data.level) {
            levelElement.className = `security-level ${data.level.toLowerCase()}`;
            levelElement.textContent = `NÍVEL: ${data.level.toUpperCase()}`;
        }
    }

    // Plugins Module Methods
    async loadPluginsData() {
        try {
            const response = await fetch('/api/plugins');
            const plugins = await response.json();
            
            this.plugins = plugins;
            this.displayPlugins(plugins);
            
        } catch (error) {
            console.error('Plugins data error:', error);
        }
    }

    displayPlugins(plugins) {
        const container = document.getElementById('pluginsGrid');
        if (!container) return;
        
        container.innerHTML = plugins.map(plugin => `
            <div class="plugin-card">
                <div class="plugin-header">
                    <div class="plugin-icon">
                        <i class="fas fa-${this.getPluginIcon(plugin.id)}"></i>
                    </div>
                    <div class="plugin-info">
                        <h3>${plugin.name}</h3>
                        <span class="plugin-status ${plugin.status}">${plugin.status.toUpperCase()}</span>
                    </div>
                </div>
                <p class="plugin-description">${plugin.description}</p>
                <div class="plugin-actions">
                    <button class="plugin-btn ${plugin.enabled ? 'enabled' : 'disabled'}" 
                            onclick="jarvis.togglePlugin('${plugin.id}')">
                        ${plugin.enabled ? 'Desativar' : 'Ativar'}
                    </button>
                </div>
            </div>
        `).join('');
    }

    getPluginIcon(pluginId) {
        const icons = {
            'assistant': 'robot',
            'vision': 'eye',
            'security': 'shield-alt',
            'weather': 'cloud-sun',
            'automation': 'home',
            'games': 'gamepad',
            'education': 'graduation-cap',
            'data': 'chart-bar'
        };
        return icons[pluginId] || 'puzzle-piece';
    }

    async togglePlugin(pluginId) {
        try {
            const response = await fetch(`/api/plugins/${pluginId}/toggle`, {
                method: 'POST'
            });
            
            if (response.ok) {
                await this.loadPluginsData();
                this.showNotification('✅', 'Plugin atualizado', 'success');
            }
        } catch (error) {
            console.error('Plugin toggle error:', error);
            this.showNotification('❌', 'Erro ao atualizar plugin', 'error');
        }
    }

    async refreshPlugins() {
        await this.loadPluginsData();
        this.showNotification('🔄', 'Plugins atualizados', 'info');
    }

    // Training Module Methods
    uploadTrainingData() {
        const input = document.createElement('input');
        input.type = 'file';
        input.multiple = true;
        input.accept = '.txt,.json,.csv,.pdf';
        
        input.onchange = (e) => {
            const files = Array.from(e.target.files);
            this.handleTrainingUpload(files);
        };
        
        input.click();
    }

    async handleTrainingUpload(files) {
        const formData = new FormData();
        
        files.forEach((file, index) => {
            formData.append(`file_${index}`, file);
        });
        
        try {
            const response = await fetch('/api/training/upload', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            this.showNotification('✅', `${files.length} arquivo(s) enviado(s)`, 'success');
            
        } catch (error) {
            console.error('Training upload error:', error);
            this.showNotification('❌', 'Erro no upload', 'error');
        }
    }

    // Analytics Module Methods
    async loadAnalyticsData() {
        await this.updateMetrics();
        this.initializeCharts();
    }

    async updateMetrics() {
        try {
            const response = await fetch('/api/metrics');
            const data = await response.json();
            
            this.metrics = data;
            this.displayMetrics(data);
            
        } catch (error) {
            console.error('Metrics error:', error);
        }
    }

    displayMetrics(metrics) {
        const elements = {
            'cpuUsage': metrics.cpuUsage,
            'ramUsage': metrics.memoryUsage,
            'diskUsage': metrics.diskUsage || '42%',
            'pluginCount': metrics.activePlugins
        };

        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        });
    }

    initializeCharts() {
        // Initialize mini charts for metrics
        const charts = ['cpuChart', 'ramChart', 'diskChart'];
        
        charts.forEach(chartId => {
            const canvas = document.getElementById(chartId);
            if (canvas) {
                this.drawMiniChart(canvas);
            }
        });
    }

    drawMiniChart(canvas) {
        const ctx = canvas.getContext('2d');
        const width = canvas.width;
        const height = canvas.height;
        
        // Generate sample data
        const data = Array.from({length: 10}, () => Math.random() * 100);
        
        ctx.clearRect(0, 0, width, height);
        ctx.strokeStyle = '#00ffff';
        ctx.lineWidth = 2;
        
        ctx.beginPath();
        data.forEach((value, index) => {
            const x = (index / (data.length - 1)) * width;
            const y = height - (value / 100) * height;
            
            if (index === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        });
        ctx.stroke();
    }

    startRealTimeUpdates() {
        // Update metrics every 5 seconds
        setInterval(() => {
            if (this.currentModule === 'analytics') {
                this.updateMetrics();
            }
        }, 5000);

        // Update charts every 2 seconds
        setInterval(() => {
            if (this.currentModule === 'analytics') {
                this.initializeCharts();
            }
        }, 2000);
    }

    // Utility Methods
    executeActions(actions) {
        actions.forEach(action => {
            switch(action.type) {
                case 'notification':
                    this.showNotification(action.title, action.message, action.level);
                    break;
                case 'switch_module':
                    this.switchModule(action.module);
                    break;
                case 'update_metrics':
                    this.displayMetrics(action.data);
                    break;
            }
        });
    }

    showNotification(title, message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <div class="notification-title">${title}</div>
                <div class="notification-message">${message}</div>
            </div>
            <button class="notification-close">&times;</button>
        `;
        
        // Add styles
        Object.assign(notification.style, {
            position: 'fixed',
            top: '100px',
            right: '20px',
            background: 'rgba(15, 15, 25, 0.95)',
            border: '1px solid #00ffff',
            borderRadius: '12px',
            padding: '1rem',
            color: '#00ffff',
            backdropFilter: 'blur(20px)',
            zIndex: '10000',
            minWidth: '300px',
            animation: 'slideIn 0.3s ease'
        });
        
        document.body.appendChild(notification);
        
        // Auto remove
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.animation = 'slideOut 0.3s ease';
                setTimeout(() => notification.remove(), 300);
            }
        }, 5000);
        
        // Manual close
        notification.querySelector('.notification-close').onclick = () => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        };
    }

    clearChat() {
        const messagesContainer = document.getElementById('chatMessages');
        messagesContainer.innerHTML = `
            <div class="system-message">
                <div class="message-icon">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="message-content">
                    <div class="message-header">
                        <span class="sender-name">JARVIS 3.0</span>
                        <span class="message-time">${new Date().toLocaleTimeString('pt-BR')}</span>
                    </div>
                    <div class="message-text">
                        Chat limpo. Como posso ajudá-lo?
                    </div>
                </div>
            </div>
        `;
        
        this.chatMessages = [];
        this.showNotification('🗑️', 'Chat limpo', 'info');
    }
}

// Global functions for onclick handlers
function toggleSettings() {
    jarvis.showNotification('⚙️', 'Configurações em desenvolvimento', 'info');
}

function toggleQuickActions() {
    const quickActions = document.getElementById('quickActions');
    jarvis.quickActionsOpen = !jarvis.quickActionsOpen;
    
    if (jarvis.quickActionsOpen) {
        quickActions.classList.add('active');
    } else {
        quickActions.classList.remove('active');
    }
}

function quickCommand(command) {
    const chatInput = document.getElementById('chatInput');
    const commands = {
        'status': 'status do sistema',
        'help': 'ajuda',
        'settings': 'configurações'
    };
    
    chatInput.value = commands[command] || command;
    jarvis.sendMessage();
    toggleQuickActions();
}

function clearChat() {
    jarvis.clearChat();
}

function toggleVoice() {
    jarvis.toggleVoice();
}

// Initialize app
function initializeApp() {
    window.jarvis = new JarvisModernInterface();
}

// Add custom CSS for animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .typing-dots {
        display: inline-flex;
        gap: 0.25rem;
        margin-right: 0.5rem;
    }
    
    .typing-dots span {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #00ffff;
        animation: typingDot 1.4s infinite;
    }
    
    .typing-dots span:nth-child(1) { animation-delay: 0s; }
    .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
    .typing-dots span:nth-child(3) { animation-delay: 0.4s; }
    
    @keyframes typingDot {
        0%, 60%, 100% { opacity: 0.3; transform: scale(0.8); }
        30% { opacity: 1; transform: scale(1); }
    }
    
    .plugin-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(0, 255, 255, 0.2);
        border-radius: 12px;
        padding: 1.5rem;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .plugin-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 255, 255, 0.2);
    }
    
    .plugin-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    
    .plugin-icon {
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(0, 255, 255, 0.1);
        border-radius: 8px;
        font-size: 1.2rem;
        color: #00ffff;
    }
    
    .plugin-info h3 {
        margin: 0;
        color: #00ffff;
        font-size: 1rem;
    }
    
    .plugin-status {
        font-size: 0.7rem;
        padding: 0.25rem 0.5rem;
        border-radius: 20px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .plugin-status.active {
        background: rgba(0, 255, 128, 0.2);
        color: #00ff80;
    }
    
    .plugin-status.idle {
        background: rgba(255, 255, 0, 0.2);
        color: #ffff00;
    }
    
    .plugin-description {
        color: rgba(255, 255, 255, 0.7);
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }
    
    .plugin-btn {
        padding: 0.5rem 1rem;
        border: 1px solid rgba(0, 255, 255, 0.2);
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.05);
        color: #00ffff;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .plugin-btn:hover {
        background: rgba(0, 255, 255, 0.1);
        transform: translateY(-2px);
    }
    
    .plugin-btn.enabled {
        background: rgba(0, 255, 128, 0.2);
        border-color: #00ff80;
        color: #00ff80;
    }
    
    .vision-result {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(0, 255, 255, 0.2);
        border-radius: 8px;
        padding: 1rem;
    }
    
    .vision-result h4 {
        color: #00ffff;
        margin-bottom: 0.5rem;
    }
    
    .detected-objects {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .object-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem;
        background: rgba(0, 0, 0, 0.3);
        border-radius: 6px;
    }
    
    .object-name {
        color: #00ffff;
        font-weight: 500;
    }
    
    .object-confidence {
        color: #00ff80;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
    }
`;
document.head.appendChild(style);

// Export for global access
window.JarvisModernInterface = JarvisModernInterface;
