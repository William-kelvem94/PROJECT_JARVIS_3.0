# JARVIS 3.0 Desktop Application

## 🚀 Como executar a versão Desktop (Electron)

### Pré-requisitos
- Node.js (versão 16 ou superior)
- NPM (incluído com Node.js)
- Python 3.8+ (para o backend)

### Instalação

1. **Navegue até a pasta desktop:**
   ```bash
   cd LocalJarvis/desktop
   ```

2. **Instale as dependências:**
   ```bash
   npm install
   ```

3. **Execute a aplicação:**
   ```bash
   npm start
   ```

### Recursos da Versão Desktop

✨ **Interface Nativa**: Janela sem bordas com design futurístico
🎨 **Transparência e Efeitos**: Vibrancy e animações suaves
⚡ **Performance Otimizada**: Aceleração de hardware habilitada
🔧 **Menu Personalizado**: Controles dedicados para IA e sistema
🖥️ **Controles de Janela**: Minimizar, maximizar, fechar personalizados
🔒 **Segurança**: Context isolation e sandboxing habilitados
📊 **Monitoramento**: Métricas do sistema em tempo real
🤖 **Backend Integrado**: Servidor Python iniciado automaticamente

### Comandos Disponíveis

- `npm start` - Inicia a aplicação em modo desenvolvimento
- `npm run build` - Constrói a aplicação para distribuição
- `npm run pack` - Empacota sem instalar
- `npm run dist` - Cria instalador para distribuição

### Teclas de Atalho

- **Ctrl+R** / **Cmd+R** - Recarregar interface
- **F11** / **Ctrl+Cmd+F** - Tela cheia
- **Ctrl+Shift+I** - Console do desenvolvedor
- **Ctrl+Q** / **Cmd+Q** - Sair da aplicação
- **Ctrl+,** - Configurações

### Estrutura da Aplicação

```
desktop/
├── main.js          # Processo principal do Electron
├── preload.js       # Script de preload para segurança
├── package.json     # Configurações e dependências
├── assets/          # Ícones e recursos
└── README.md        # Este arquivo
```

### Personalizações

A aplicação desktop inclui:
- Frame customizado sem barra de título
- Transparência e efeitos visuais
- Menu contextual personalizado
- Integração com o sistema operacional
- Notificações nativas
- Controle automático do backend

### Problemas Conhecidos

- No Windows, pode ser necessário executar como administrador na primeira vez
- No macOS, pode aparecer aviso de segurança (normal para apps não assinados)
- No Linux, certifique-se de ter as dependências gráficas instaladas

### Suporte

Para reportar problemas ou solicitar recursos, abra uma issue no repositório do projeto.
