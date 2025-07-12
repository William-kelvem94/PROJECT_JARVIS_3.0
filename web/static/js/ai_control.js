/**
 * JARVIS AI Control Center - Advanced JavaScript Controller
 * Integração completa com Ollama e backend Python
 */

class AIControlCenter {
    constructor() {
        this.currentModel = 'jarvis-personal';
        this.currentPersonality = 'assistant';
        this.availableModels = [];
        this.isStreaming = false;
        this.socket = null;
        
        // Model configurations
        this.modelConfigs = {
            'jarvis-personal': {
                type: 'Personalizado',
                size: '4.1GB',
                specialty: 'Assistente Geral',
                description: 'Modelo personalizado do JARVIS otimizado para tarefas gerais',
                tags: ['Geral', 'Personalizado', 'Rápido']
            },
            'mixtral': {
                type: 'Mixture of Experts',
                size: '26GB',
                specialty: 'Análise Complexa',
                description: 'Modelo avançado para raciocínio complexo e múltiplas tarefas',
                tags: ['Avançado', 'Raciocínio', 'Múltiplas Tarefas']
            },
            'deepseek-coder': {
                type: 'Code Specialist',
                size: '776MB',
                specialty: 'Programação',
                description: 'Especializado em desenvolvimento e debug de código',
                tags: ['Código', 'Debug', 'Desenvolvimento']
            },
            'mistral': {
                type: 'General Purpose',
                size: '4.1GB',
                specialty: 'Texto e Criatividade',
                description: 'Excelente para texto criativo e tarefas linguísticas',
                tags: ['Criativo', 'Texto', 'Linguagem']
            },
            'phi3': {
                type: 'Compact',
                size: '2.3GB',
                specialty: 'Eficiência',
                description: 'Modelo compacto e eficiente para tarefas rápidas',
                tags: ['Compacto', 'Rápido', 'Eficiente']
            },
            'codellama': {
                type: 'Code Specialist',
                size: '3.8GB',
                specialty: 'Código Avançado',
                description: 'Especialista em geração e análise de código',
                tags: ['Código', 'Análise', 'Geração']
            }
        };

        // Personality descriptions
        this.personalities = {
            'assistant': 'Assistente equilibrado para tarefas gerais',
            'creative': 'Foco em criatividade, arte e escrita imaginativa',
            'analytical': 'Análise detalhada, dados e raciocínio lógico',
            'technical': 'Especialista técnico em desenvolvimento e engenharia',
            'friendly': 'Conversacional, amigável e acessível',
            'professional': 'Formal e profissional para ambiente corporativo',
            'expert': 'Conhecimento profundo e especializado'
        };

        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeSocket();
        this.loadModels();
        this.updatePersonalityDescription();
        this.startStatusUpdates();
    }

    setupEventListeners() {
        // Model selection
        document.getElementById('active-model')?.addEventListener('change', (e) => {
            this.selectModel(e.target.value);
        });

        // Personality selection
        document.getElementById('personality')?.addEventListener('change', (e) => {
            this.selectPersonality(e.target.value);
        });

        // Chat functionality
        document.getElementById('send-message')?.addEventListener('click', () => {
            this.sendMessage();
        });

        document.getElementById('chat-input')?.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Clear chat
        document.getElementById('clear-chat')?.addEventListener('click', () => {
            this.clearChat();
        });

        // Refresh models
        document.getElementById('refresh-models')?.addEventListener('click', () => {
            this.loadModels();
        });

        // Quick model selection
        document.querySelectorAll('.quick-model').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const model = e.target.dataset.model;
                this.selectModel(model);
                this.updateQuickModelButtons(model);
            });
        });

        // AI Tools
        document.querySelectorAll('.tool-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tool = e.currentTarget.dataset.tool;
                this.activateTool(tool);
            });
        });

        // Download models
        document.getElementById('download-models')?.addEventListener('click', () => {
            this.downloadRecommendedModels();
        });
    }

    initializeSocket() {
        if (typeof io !== 'undefined') {
            this.socket = io();
            
            this.socket.on('connect', () => {
                console.log('Connected to JARVIS backend');
                this.updateAIStatus('online', 'Conectado');
            });

            this.socket.on('disconnect', () => {
                console.log('Disconnected from JARVIS backend');
                this.updateAIStatus('offline', 'Desconectado');
            });

            this.socket.on('ai_response', (data) => {
                this.handleAIResponse(data);
            });

            this.socket.on('model_status', (data) => {
                this.updateModelStatus(data);
            });
        }
    }

    async loadModels() {
        try {
            this.showLoading('models-grid');
            
            const response = await fetch('/api/ai/models');
            const data = await response.json();
            
            if (data.success) {
                this.availableModels = data.models;
                this.renderModelsGrid();
                this.updateModelSelect();
                this.updateStatus('loaded-models-count', this.availableModels.length);
            } else {
                throw new Error(data.error || 'Erro ao carregar modelos');
            }
        } catch (error) {
            console.error('Erro ao carregar modelos:', error);
            this.showError('Erro ao carregar modelos: ' + error.message);
        } finally {
            this.hideLoading('models-grid');
        }
    }

    renderModelsGrid() {
        const grid = document.getElementById('models-grid');
        if (!grid) return;

        grid.innerHTML = '';

        this.availableModels.forEach(model => {
            const config = this.modelConfigs[model.name] || {
                type: 'Desconhecido',
                size: model.size || 'N/A',
                specialty: 'Geral',
                description: `Modelo ${model.name}`,
                tags: ['Modelo']
            };

            const modelCard = document.createElement('div');
            modelCard.className = `model-card ${model.name === this.currentModel ? 'active' : ''}`;
            modelCard.dataset.model = model.name;
            
            modelCard.innerHTML = `
                <div class="model-name">${model.name}</div>
                <div class="model-description">${config.description}</div>
                <div class="model-tags">
                    ${config.tags.map(tag => `<span class="model-tag">${tag}</span>`).join('')}
                </div>
                <div class="model-status">
                    <div class="status-indicator">
                        <span class="status-light ${model.loaded ? '' : 'loading'}"></span>
                        <span>${model.loaded ? 'Carregado' : 'Disponível'}</span>
                    </div>
                    <div class="model-size">${config.size}</div>
                </div>
            `;

            modelCard.addEventListener('click', () => {
                this.selectModel(model.name);
            });

            grid.appendChild(modelCard);
        });
    }

    updateModelSelect() {
        const select = document.getElementById('active-model');
        if (!select) return;

        select.innerHTML = '<option value="">Selecione um modelo...</option>';
        
        this.availableModels.forEach(model => {
            const option = document.createElement('option');
            option.value = model.name;
            option.textContent = model.name;
            option.selected = model.name === this.currentModel;
            select.appendChild(option);
        });
    }

    selectModel(modelName) {
        if (!modelName || modelName === this.currentModel) return;

        this.currentModel = modelName;
        
        // Update UI
        this.updateModelInfo(modelName);
        this.updateModelCards(modelName);
        this.updateChatModelIndicator(modelName);
        this.updateQuickModelButtons(modelName);
        
        // Update select
        const select = document.getElementById('active-model');
        if (select) select.value = modelName;

        console.log(`Modelo selecionado: ${modelName}`);
    }

    updateModelInfo(modelName) {
        const config = this.modelConfigs[modelName] || {};
        
        const typeEl = document.getElementById('model-type');
        const sizeEl = document.getElementById('model-size');
        const specialtyEl = document.getElementById('model-specialty');
        
        if (typeEl) typeEl.textContent = config.type || 'N/A';
        if (sizeEl) sizeEl.textContent = config.size || 'N/A';
        if (specialtyEl) specialtyEl.textContent = config.specialty || 'N/A';
    }

    updateModelCards(selectedModel) {
        document.querySelectorAll('.model-card').forEach(card => {
            card.classList.toggle('active', card.dataset.model === selectedModel);
        });
    }

    updateChatModelIndicator(modelName) {
        const indicator = document.getElementById('chat-model-indicator');
        if (indicator) {
            indicator.textContent = modelName.toUpperCase();
        }
    }

    updateQuickModelButtons(selectedModel) {
        document.querySelectorAll('.quick-model').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.model === selectedModel);
        });
    }

    selectPersonality(personality) {
        this.currentPersonality = personality;
        this.updatePersonalityDescription();
        console.log(`Personalidade selecionada: ${personality}`);
    }

    updatePersonalityDescription() {
        const description = document.getElementById('personality-description');
        if (description) {
            description.textContent = this.personalities[this.currentPersonality] || 'Personalidade personalizada';
        }
    }

    async sendMessage() {
        const input = document.getElementById('chat-input');
        const message = input?.value.trim();
        
        if (!message) return;

        // Add user message to chat
        this.addMessage('user', message);
        input.value = '';

        // Show typing indicator
        const typingId = this.addTypingIndicator();

        try {
            const response = await fetch('/api/ai/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    model: this.currentModel,
                    personality: this.currentPersonality,
                    stream: document.getElementById('stream-mode')?.checked || false
                })
            });

            const data = await response.json();
            
            // Remove typing indicator
            this.removeTypingIndicator(typingId);

            if (data.success) {
                this.addMessage('ai', data.response);
                this.updateLastResponseTime();
            } else {
                throw new Error(data.error || 'Erro na resposta da IA');
            }
        } catch (error) {
            console.error('Erro ao enviar mensagem:', error);
            this.removeTypingIndicator(typingId);
            this.addMessage('ai', '❌ Erro: ' + error.message);
        }
    }

    addMessage(sender, content) {
        const messagesContainer = document.getElementById('chat-messages');
        if (!messagesContainer) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const avatar = sender === 'ai' ? '🤖' : '👤';
        const senderName = sender === 'ai' ? 'JARVIS' : 'Você';
        
        messageDiv.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div class="message-content">
                <strong>${senderName}:</strong> ${content}
            </div>
        `;

        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    addTypingIndicator() {
        const id = 'typing-' + Date.now();
        const messagesContainer = document.getElementById('chat-messages');
        if (!messagesContainer) return id;

        const typingDiv = document.createElement('div');
        typingDiv.id = id;
        typingDiv.className = 'message ai-message';
        typingDiv.innerHTML = `
            <div class="message-avatar">🤖</div>
            <div class="message-content">
                <strong>JARVIS:</strong> <span class="typing-indicator">Digitando...</span>
            </div>
        `;

        messagesContainer.appendChild(typingDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        return id;
    }

    removeTypingIndicator(id) {
        const element = document.getElementById(id);
        if (element) {
            element.remove();
        }
    }

    clearChat() {
        const messagesContainer = document.getElementById('chat-messages');
        if (messagesContainer) {
            messagesContainer.innerHTML = `
                <div class="message ai-message">
                    <div class="message-avatar">🤖</div>
                    <div class="message-content">
                        <strong>JARVIS:</strong> Chat limpo! Como posso ajudar?
                    </div>
                </div>
            `;
        }
    }

    activateTool(toolName) {
        const toolActions = {
            'code': () => this.openCodeGenerator(),
            'analyze': () => this.openTextAnalyzer(),
            'translate': () => this.openTranslator(),
            'summarize': () => this.openSummarizer(),
            'explain': () => this.openExplainer(),
            'debug': () => this.openDebugger()
        };

        if (toolActions[toolName]) {
            toolActions[toolName]();
        }
    }

    openCodeGenerator() {
        const message = "🔧 Modo Gerador de Código ativado! Descreva o que você quer programar:";
        this.addMessage('ai', message);
        
        // Switch to code-specialized model if available
        if (this.availableModels.find(m => m.name === 'deepseek-coder')) {
            this.selectModel('deepseek-coder');
        }
        
        document.getElementById('chat-input').focus();
    }

    openTextAnalyzer() {
        const message = "📊 Modo Analisador de Texto ativado! Cole o texto que deseja analisar:";
        this.addMessage('ai', message);
        this.selectPersonality('analytical');
        document.getElementById('chat-input').focus();
    }

    openTranslator() {
        const message = "🌐 Modo Tradutor ativado! Especifique os idiomas e o texto a traduzir:";
        this.addMessage('ai', message);
        document.getElementById('chat-input').focus();
    }

    openSummarizer() {
        const message = "📝 Modo Resumidor ativado! Cole o texto que deseja resumir:";
        this.addMessage('ai', message);
        this.selectPersonality('analytical');
        document.getElementById('chat-input').focus();
    }

    openExplainer() {
        const message = "💡 Modo Explicador ativado! O que você gostaria que eu explicasse?";
        this.addMessage('ai', message);
        this.selectPersonality('expert');
        document.getElementById('chat-input').focus();
    }

    openDebugger() {
        const message = "🐛 Modo Debug ativado! Cole seu código com erro:";
        this.addMessage('ai', message);
        
        // Switch to code model
        if (this.availableModels.find(m => m.name === 'deepseek-coder')) {
            this.selectModel('deepseek-coder');
        }
        
        this.selectPersonality('technical');
        document.getElementById('chat-input').focus();
    }

    async downloadRecommendedModels() {
        const recommendedModels = ['mixtral', 'deepseek-coder', 'mistral', 'phi3'];
        const button = document.getElementById('download-models');
        
        if (button) {
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Baixando...';
        }

        try {
            const response = await fetch('/api/ai/download-models', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ models: recommendedModels })
            });

            const data = await response.json();
            
            if (data.success) {
                this.showSuccess('Download iniciado! Acompanhe o progresso no terminal.');
                this.startDownloadProgress();
            } else {
                throw new Error(data.error || 'Erro ao iniciar download');
            }
        } catch (error) {
            console.error('Erro no download:', error);
            this.showError('Erro no download: ' + error.message);
        } finally {
            if (button) {
                button.disabled = false;
                button.innerHTML = '<i class="fas fa-download"></i> Baixar Modelos Recomendados';
            }
        }
    }

    startStatusUpdates() {
        // Update AI status every 30 seconds
        setInterval(() => {
            this.checkAIStatus();
        }, 30000);

        // Initial check
        this.checkAIStatus();
    }

    async checkAIStatus() {
        try {
            const response = await fetch('/api/ai/status');
            const data = await response.json();
            
            if (data.success) {
                this.updateAIStatus('online', 'Online');
                this.updateOllamaStatus(data.ollama_status);
            } else {
                this.updateAIStatus('warning', 'Problemas');
            }
        } catch (error) {
            console.error('Erro ao verificar status:', error);
            this.updateAIStatus('error', 'Offline');
        }
    }

    updateAIStatus(status, text) {
        const light = document.getElementById('ai-status-light');
        const textEl = document.getElementById('ai-status-text');
        
        if (light) {
            light.className = `status-light ${status}`;
        }
        
        if (textEl) {
            textEl.textContent = text;
        }
    }

    updateOllamaStatus(status) {
        const statusBadge = document.getElementById('ollama-status');
        const gpuMemory = document.getElementById('gpu-memory');
        
        if (statusBadge) {
            statusBadge.textContent = status.running ? 'Online' : 'Offline';
            statusBadge.className = `status-badge ${status.running ? '' : 'error'}`;
        }
        
        if (gpuMemory && status.gpu_memory) {
            gpuMemory.textContent = status.gpu_memory;
        }
    }

    updateLastResponseTime() {
        const timeEl = document.getElementById('last-response-time');
        if (timeEl) {
            timeEl.textContent = new Date().toLocaleTimeString();
        }
    }

    updateStatus(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
        }
    }

    showLoading(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.classList.add('loading');
        }
    }

    hideLoading(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.classList.remove('loading');
        }
    }

    showSuccess(message) {
        // Implement success notification
        console.log('Success:', message);
    }

    showError(message) {
        // Implement error notification
        console.error('Error:', message);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.aiControl = new AIControlCenter();
    console.log('🤖 JARVIS AI Control Center initialized');
});
