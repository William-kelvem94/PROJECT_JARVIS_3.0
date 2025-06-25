const { app, BrowserWindow, Menu, ipcMain, shell, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

class JarvisDesktop {
    constructor() {
        this.mainWindow = null;
        this.backendProcess = null;
        this.isQuitting = false;
    }

    createWindow() {
        // Cria a janela principal
        this.mainWindow = new BrowserWindow({
            width: 1400,
            height: 900,
            minWidth: 1200,
            minHeight: 800,
            show: false,
            icon: path.join(__dirname, 'assets', 'icon.png'),
            frame: false, // Remove a barra de título padrão
            transparent: true,
            webPreferences: {
                nodeIntegration: false,
                contextIsolation: true,
                enableRemoteModule: false,
                preload: path.join(__dirname, 'preload.js'),
                webSecurity: false // Para desenvolvimento local
            },
            titleBarStyle: 'hidden',
            backgroundThrottling: false,
            show: false
        });

        // Carrega a interface
        this.mainWindow.loadFile(path.join(__dirname, '..', 'frontend', 'index.html'));

        // Mostra a janela quando estiver pronta
        this.mainWindow.once('ready-to-show', () => {
            this.mainWindow.show();
            
            // Adiciona efeitos visuais
            this.mainWindow.setVibrancy('ultra-dark');
            
            // Animação de entrada
            this.mainWindow.setOpacity(0);
            let opacity = 0;
            const fadeIn = setInterval(() => {
                opacity += 0.05;
                this.mainWindow.setOpacity(opacity);
                if (opacity >= 1) {
                    clearInterval(fadeIn);
                }
            }, 20);
        });

        // Eventos da janela
        this.mainWindow.on('closed', () => {
            this.mainWindow = null;
        });

        this.mainWindow.on('close', (event) => {
            if (!this.isQuitting) {
                event.preventDefault();
                this.mainWindow.hide();
            }
        });

        // Menu personalizado
        this.createMenu();
        
        // Configurações de desenvolvimento
        if (process.env.NODE_ENV === 'development') {
            this.mainWindow.webContents.openDevTools();
        }
    }

    createMenu() {
        const template = [
            {
                label: 'JARVIS',
                submenu: [
                    {
                        label: 'Sobre o JARVIS 3.0',
                        click: () => {
                            dialog.showMessageBox(this.mainWindow, {
                                type: 'info',
                                title: 'Sobre o JARVIS 3.0',
                                message: 'JARVIS 3.0 - Advanced AI Assistant',
                                detail: 'Sistema de Inteligência Artificial Avançado\\nVersão 3.0.0\\n\\nDesenvolvido para fornecer assistência inteligente com recursos de visão computacional, segurança, plugins avançados e muito mais.',
                                icon: path.join(__dirname, 'assets', 'icon.png')
                            });
                        }
                    },
                    { type: 'separator' },
                    {
                        label: 'Configurações',
                        accelerator: 'CmdOrCtrl+,',
                        click: () => {
                            // TODO: Abrir painel de configurações
                        }
                    },
                    { type: 'separator' },
                    {
                        label: 'Sair',
                        accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
                        click: () => {
                            this.isQuitting = true;
                            app.quit();
                        }
                    }
                ]
            },
            {
                label: 'Sistema',
                submenu: [
                    {
                        label: 'Reiniciar Backend',
                        click: () => {
                            this.restartBackend();
                        }
                    },
                    {
                        label: 'Monitor do Sistema',
                        click: () => {
                            // TODO: Abrir monitor do sistema
                        }
                    },
                    { type: 'separator' },
                    {
                        label: 'Logs do Sistema',
                        click: () => {
                            // TODO: Abrir logs
                        }
                    }
                ]
            },
            {
                label: 'IA',
                submenu: [
                    {
                        label: 'Treinar Modelo',
                        click: () => {
                            // TODO: Iniciar treinamento
                        }
                    },
                    {
                        label: 'Carregar Modelo',
                        click: () => {
                            // TODO: Carregar modelo
                        }
                    },
                    { type: 'separator' },
                    {
                        label: 'Plugins',
                        click: () => {
                            // TODO: Gerenciar plugins
                        }
                    }
                ]
            },
            {
                label: 'Ferramentas',
                submenu: [
                    {
                        label: 'Console do Desenvolvedor',
                        accelerator: process.platform === 'darwin' ? 'Alt+Cmd+I' : 'Ctrl+Shift+I',
                        click: () => {
                            this.mainWindow.webContents.toggleDevTools();
                        }
                    },
                    {
                        label: 'Recarregar',
                        accelerator: 'CmdOrCtrl+R',
                        click: () => {
                            this.mainWindow.reload();
                        }
                    },
                    { type: 'separator' },
                    {
                        label: 'Tela Cheia',
                        accelerator: process.platform === 'darwin' ? 'Ctrl+Cmd+F' : 'F11',
                        click: () => {
                            this.mainWindow.setFullScreen(!this.mainWindow.isFullScreen());
                        }
                    }
                ]
            },
            {
                label: 'Ajuda',
                submenu: [
                    {
                        label: 'Documentação',
                        click: () => {
                            shell.openExternal('https://github.com/jarvis-ai/docs');
                        }
                    },
                    {
                        label: 'Reportar Bug',
                        click: () => {
                            shell.openExternal('https://github.com/jarvis-ai/issues');
                        }
                    }
                ]
            }
        ];

        const menu = Menu.buildFromTemplate(template);
        Menu.setApplicationMenu(menu);
    }

    startBackend() {
        try {
            // Inicia o servidor Python
            const backendPath = path.join(__dirname, '..', 'simple_server.py');
            this.backendProcess = spawn('python', [backendPath], {
                cwd: path.join(__dirname, '..'),
                stdio: 'pipe'
            });

            this.backendProcess.stdout.on('data', (data) => {
                console.log(`Backend: ${data}`);
            });

            this.backendProcess.stderr.on('data', (data) => {
                console.error(`Backend Error: ${data}`);
            });

            this.backendProcess.on('close', (code) => {
                console.log(`Backend process exited with code ${code}`);
            });

            console.log('Backend iniciado com sucesso!');
        } catch (error) {
            console.error('Erro ao iniciar backend:', error);
            dialog.showErrorBox('Erro', 'Não foi possível iniciar o backend do JARVIS. Verifique se o Python está instalado.');
        }
    }

    restartBackend() {
        if (this.backendProcess) {
            this.backendProcess.kill();
        }
        setTimeout(() => {
            this.startBackend();
        }, 1000);
    }

    setupIPC() {
        // Comunicação entre renderer e main process
        ipcMain.handle('get-system-info', async () => {
            const os = require('os');
            return {
                platform: process.platform,
                arch: process.arch,
                cpu: os.cpus()[0].model,
                totalMemory: os.totalmem(),
                freeMemory: os.freemem(),
                uptime: os.uptime()
            };
        });

        ipcMain.handle('minimize-window', () => {
            this.mainWindow.minimize();
        });

        ipcMain.handle('maximize-window', () => {
            if (this.mainWindow.isMaximized()) {
                this.mainWindow.unmaximize();
            } else {
                this.mainWindow.maximize();
            }
        });

        ipcMain.handle('close-window', () => {
            this.mainWindow.close();
        });
    }

    init() {
        // Configurações do app
        app.setName('JARVIS 3.0');
        
        // Previne múltiplas instâncias
        const gotTheLock = app.requestSingleInstanceLock();
        
        if (!gotTheLock) {
            app.quit();
            return;
        }

        app.on('second-instance', () => {
            if (this.mainWindow) {
                if (this.mainWindow.isMinimized()) this.mainWindow.restore();
                this.mainWindow.focus();
            }
        });

        // Quando o Electron terminar de inicializar
        app.whenReady().then(() => {
            this.createWindow();
            this.setupIPC();
            this.startBackend();

            app.on('activate', () => {
                if (BrowserWindow.getAllWindows().length === 0) {
                    this.createWindow();
                }
            });
        });

        // Encerra quando todas as janelas são fechadas
        app.on('window-all-closed', () => {
            if (process.platform !== 'darwin') {
                app.quit();
            }
        });

        // Limpa recursos quando o app for fechado
        app.on('before-quit', () => {
            this.isQuitting = true;
            if (this.backendProcess) {
                this.backendProcess.kill();
            }
        });

        // Configurações de segurança
        app.on('web-contents-created', (event, contents) => {
            contents.on('new-window', (navigationEvent, navigationURL) => {
                navigationEvent.preventDefault();
                shell.openExternal(navigationURL);
            });
        });
    }
}

// Inicia a aplicação
const jarvisApp = new JarvisDesktop();
jarvisApp.init();
