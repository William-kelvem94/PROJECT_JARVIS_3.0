// JARVIS 3.0 - Chat JavaScript

class JarvisChat {
    constructor() {
        this.socket = io();
        this.isConnected = false;
        this.currentPersonality = 'assistente';
        this.personalities = [];
        this.currentMessageTimeout = null; // CORREÇÃO: Timeout para mensagens
        
        this.init();
    }
    
    init() {
        this.setupElements();
        this.setupSocketEvents();
        this.setupEventListeners();
        this.loadPersonalities();
        this.startSystemMonitoring();
    }
    
    setupElements() {
        this.chatMessages = document.getElementById('chat-messages');
        this.chatInput = document.getElementById('chat-input');
        this.sendBtn = document.getElementById('send-btn');
        this.personalityDisplay = document.getElementById('personality-display');
        this.personalityModal = document.getElementById('personality-modal');
    }
    
    setupSocketEvents() {
        this.socket.on('connect', () => {
            console.log('🔗 Conectado ao chat');
            this.isConnected = true;
            this.updateConnectionStatus(true);
        });
        
        this.socket.on('disconnect', () => {
            console.log('❌ Desconectado do chat');
            this.isConnected = false;
            this.updateConnectionStatus(false);
        });
        
        this.socket.on('chat_response', (data) => {
            // CORREÇÃO: Limpar timeout se resposta chegou
            if (this.currentMessageTimeout) {
                clearTimeout(this.currentMessageTimeout);
                this.currentMessageTimeout = null;
            }
            
            this.addMessage(data.response, 'assistant');
            this.hideTypingIndicator();
        });
        
        this.socket.on('chat_error', (data) => {
            // CORREÇÃO: Limpar timeout se erro chegou
            if (this.currentMessageTimeout) {
                clearTimeout(this.currentMessageTimeout);
                this.currentMessageTimeout = null;
            }
            
            this.addMessage('❌ Erro: ' + (data.error || 'Erro desconhecido'), 'system');
            this.hideTypingIndicator();
            console.error('Erro no chat:', data.error);
        });
        
        this.socket.on('system_update', (data) => {
            this.updateQuickStats(data);
        });
    }
    
    setupEventListeners() {
        // Envio de mensagem
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        
        // Enter para enviar
        this.chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Auto-resize do textarea
        this.chatInput.addEventListener('input', () => {
            this.autoResizeTextarea();
        });
        
        // Botões de controle
        document.getElementById('personality-btn')?.addEventListener('click', () => {
            this.openPersonalityModal();
        });
        
        document.getElementById('clear-chat-btn')?.addEventListener('click', () => {
            this.clearChat();
        });
        
        // Botões da toolbar
        document.getElementById('voice-btn')?.addEventListener('click', () => {
            this.toggleVoiceInput();
        });
        
        document.getElementById('attachment-btn')?.addEventListener('click', () => {
            this.handleAttachment();
        });
        
        document.getElementById('emoji-btn')?.addEventListener('click', () => {
            this.toggleEmojiPicker();
        });
    }
    
    async loadPersonalities() {
        try {
            const response = await fetch('/api/ai/personalities');
            const data = await response.json();
            
            if (data.success) {
                this.personalities = data.personalities;
                this.currentPersonality = data.current;
                this.updatePersonalityDisplay();
                this.renderPersonalityOptions();
            }
        } catch (error) {
            console.error('Erro ao carregar personalidades:', error);
        }
    }
    
    updatePersonalityDisplay() {
        const personality = this.personalities.find(p => p.id === this.currentPersonality);
        if (personality && this.personalityDisplay) {
            this.personalityDisplay.textContent = personality.name;
        }
    }
    
    renderPersonalityOptions() {
        const container = document.getElementById('personality-options');
        const listContainer = document.getElementById('personality-list');
        
        if (!container || !this.personalities.length) return;
        
        // Sidebar options
        container.innerHTML = '';
        this.personalities.forEach(personality => {
            const option = document.createElement('button');
            option.className = `personality-option ${personality.id === this.currentPersonality ? 'active' : ''}`;
            option.textContent = personality.name;
            option.onclick = () => this.changePersonality(personality.id);
            container.appendChild(option);
        });
        
        // Modal list
        if (listContainer) {
            listContainer.innerHTML = '';
            this.personalities.forEach(personality => {
                const card = document.createElement('div');
                card.className = `personality-card ${personality.id === this.currentPersonality ? 'selected' : ''}`;
                card.innerHTML = `
                    <div class="personality-name">${personality.name}</div>
                    <div class="personality-description">${personality.description}</div>
                `;
                card.onclick = () => {
                    this.changePersonality(personality.id);
                    this.closePersonalityModal();
                };
                listContainer.appendChild(card);
            });
        }
    }
    
    async changePersonality(personalityId) {
        try {
            const response = await fetch('/api/ai/personality', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ personality: personalityId })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.currentPersonality = data.current_personality;
                this.updatePersonalityDisplay();
                this.renderPersonalityOptions();
                
                const personality = this.personalities.find(p => p.id === personalityId);
                this.addMessage(`Personalidade alterada para: ${personality.name}`, 'system');
            }
        } catch (error) {
            console.error('Erro ao alterar personalidade:', error);
        }
    }
    
    sendMessage() {
        const message = this.chatInput.value.trim();
        if (!message || !this.isConnected) return;
        
        // CORREÇÃO: Validar se não há outra mensagem sendo processada
        if (document.getElementById('typing-indicator')) {
            this.addMessage('⚠️ Aguarde a resposta anterior antes de enviar nova mensagem.', 'system');
            return;
        }
        
        // Adiciona mensagem do usuário
        this.addMessage(message, 'user');
        
        // Limpa input
        this.chatInput.value = '';
        this.autoResizeTextarea();
        
        // Mostra indicador de digitação
        this.showTypingIndicator();
        
        // CORREÇÃO: Adicionar timeout para resposta
        const messageTimeout = setTimeout(() => {
            this.hideTypingIndicator();
            this.addMessage('⏰ Timeout: A IA demorou para responder. Tente novamente.', 'system');
        }, 45000); // 45 segundos timeout
        
        // Armazenar timeout para cancelar se necessário
        this.currentMessageTimeout = messageTimeout;
        
        // Envia via WebSocket
        this.socket.emit('chat_message', { message });
        
        // Log de atividade
        this.addActivityLog(`Enviou: "${message.substring(0, 30)}..."`);
    }
    
    addMessage(text, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        
        // Definir avatar baseado no tipo
        let avatarText;
        if (type === 'user') {
            avatarText = '👤';
        } else if (type === 'system') {
            avatarText = '⚙️';
        } else {
            avatarText = '🤖';
        }
        avatar.textContent = avatarText;
        
        const content = document.createElement('div');
        content.className = 'message-content';
        
        const messageText = document.createElement('div');
        messageText.className = 'message-text';
        messageText.textContent = text;
        
        const messageTime = document.createElement('div');
        messageTime.className = 'message-time';
        messageTime.textContent = new Date().toLocaleTimeString();
        
        content.appendChild(messageText);
        content.appendChild(messageTime);
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'typing-indicator';
        indicator.id = 'typing-indicator';
        indicator.innerHTML = `
            <div class="message-avatar">🤖</div>
            <div class="message-content">
                <div class="message-text">
                    JARVIS está digitando
                    <div class="typing-dots">
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                    </div>
                </div>
            </div>
        `;
        
        this.chatMessages.appendChild(indicator);
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    autoResizeTextarea() {
        this.chatInput.style.height = 'auto';
        this.chatInput.style.height = Math.min(this.chatInput.scrollHeight, 120) + 'px';
    }
    
    clearChat() {
        if (confirm('Tem certeza que deseja limpar o chat?')) {
            this.chatMessages.innerHTML = `
                <div class="message assistant-message welcome-message">
                    <div class="message-avatar">🤖</div>
                    <div class="message-content">
                        <div class="message-text">
                            Chat limpo! Como posso ajudar você agora?
                        </div>
                        <div class="message-time">${new Date().toLocaleTimeString()}</div>
                    </div>
                </div>
            `;
        }
    }
    
    updateConnectionStatus(connected) {
        const statusIndicator = document.querySelector('.status-indicator');
        const statusTitle = document.querySelector('.status-title');
        
        if (statusIndicator) {
            statusIndicator.className = `status-indicator ${connected ? 'online' : 'offline'}`;
        }
        
        if (statusTitle) {
            statusTitle.textContent = connected ? 'JARVIS Online' : 'JARVIS Offline';
        }
    }
    
    updateQuickStats(data) {
        const cpuElement = document.getElementById('quick-cpu');
        const memoryElement = document.getElementById('quick-memory');
        const batteryElement = document.getElementById('quick-battery');
        
        if (cpuElement) {
            cpuElement.textContent = `${Math.round(data.cpu_percent)}%`;
        }
        
        if (memoryElement) {
            memoryElement.textContent = `${Math.round(data.memory_percent)}%`;
        }
        
        if (batteryElement) {
            batteryElement.textContent = data.battery_percent ? 
                `${Math.round(data.battery_percent)}%` : 'N/A';
        }
    }
    
    startSystemMonitoring() {
        // Solicita monitoramento do sistema
        this.socket.emit('start_monitoring');
    }
    
    addActivityLog(text) {
        const activityLog = document.getElementById('activity-log');
        if (!activityLog) return;
        
        const item = document.createElement('div');
        item.className = 'activity-item';
        item.innerHTML = `
            <span class="activity-time">${new Date().toLocaleTimeString()}</span>
            <span class="activity-text">${text}</span>
        `;
        
        activityLog.insertBefore(item, activityLog.firstChild);
        
        // Limita a 10 itens
        const items = activityLog.querySelectorAll('.activity-item');
        if (items.length > 10) {
            items[items.length - 1].remove();
        }
    }
    
    openPersonalityModal() {
        this.personalityModal.classList.add('active');
    }
    
    closePersonalityModal() {
        this.personalityModal.classList.remove('active');
    }
    
    toggleVoiceInput() {
        // Implementar reconhecimento de voz
        this.addMessage('Reconhecimento de voz em desenvolvimento', 'system');
    }
    
    handleAttachment() {
        // Implementar anexos
        this.addMessage('Funcionalidade de anexos em desenvolvimento', 'system');
    }
    
    toggleEmojiPicker() {
        // Implementar seletor de emoji
        const emojis = ['😊', '👍', '❤️', '😂', '🤔', '👏', '🎉', '🔥'];
        const randomEmoji = emojis[Math.floor(Math.random() * emojis.length)];
        this.chatInput.value += randomEmoji;
        this.autoResizeTextarea();
    }
}

// Funções globais
function sendQuickMessage(message) {
    if (window.jarvisChat) {
        window.jarvisChat.chatInput.value = message;
        window.jarvisChat.sendMessage();
    }
}

function closePersonalityModal() {
    if (window.jarvisChat) {
        window.jarvisChat.closePersonalityModal();
    }
}

// Inicializa chat quando a página carrega
document.addEventListener('DOMContentLoaded', () => {
    window.jarvisChat = new JarvisChat();
});

// Event listeners para modal
document.addEventListener('click', (e) => {
    const modal = document.getElementById('personality-modal');
    if (e.target === modal) {
        closePersonalityModal();
    }
});

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closePersonalityModal();
    }
});
