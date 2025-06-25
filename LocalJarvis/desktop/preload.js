const { contextBridge, ipcRenderer } = require('electron');

// Expõe APIs seguras para o renderer process
contextBridge.exposeInMainWorld('electronAPI', {
    // Informações do sistema
    getSystemInfo: () => ipcRenderer.invoke('get-system-info'),
    
    // Controles da janela
    minimizeWindow: () => ipcRenderer.invoke('minimize-window'),
    maximizeWindow: () => ipcRenderer.invoke('maximize-window'),
    closeWindow: () => ipcRenderer.invoke('close-window'),
    
    // Utilitários
    platform: process.platform,
    
    // Eventos
    onMenuAction: (callback) => {
        ipcRenderer.on('menu-action', callback);
    },
    
    // Sistema
    openDevTools: () => ipcRenderer.invoke('open-dev-tools'),
    
    // Arquivos
    openFileDialog: () => ipcRenderer.invoke('open-file-dialog'),
    saveFileDialog: () => ipcRenderer.invoke('save-file-dialog'),
    
    // Notificações
    showNotification: (title, body) => ipcRenderer.invoke('show-notification', title, body)
});

// Informações sobre o ambiente
contextBridge.exposeInMainWorld('appInfo', {
    name: 'JARVIS 3.0',
    version: '3.0.0',
    isElectron: true,
    isDevelopment: process.env.NODE_ENV === 'development'
});

// Console melhorado para debug
contextBridge.exposeInMainWorld('console', {
    log: (...args) => console.log('[RENDERER]', ...args),
    error: (...args) => console.error('[RENDERER]', ...args),
    warn: (...args) => console.warn('[RENDERER]', ...args),
    info: (...args) => console.info('[RENDERER]', ...args)
});
