# LocalJarvis

Um assistente virtual local, inspirado no Jarvis do Homem de Ferro, que processa comandos de voz ou texto, executa ações no sistema e mantém histórico conversacional. Tudo roda em Docker, sem APIs pagas.

## Pré-requisitos

- Docker Desktop (Windows/macOS) ou Docker Engine (Linux).
- 8 GB RAM (mínimo).

## Instalação

1. Clone o repositório:
   ```bash
   git clone <URL_DO_REPOSITORIO>
   cd LocalJarvis
   ```

2. Inicie os containers:
   ```bash
   docker-compose up --build -d
   ```

## Uso

- **Web**: Acesse `http://localhost:5000` e use o chat.
- **API**:
  - Texto: `curl -X POST -H "Content-Type: application/json" -d '{"text":"abrir notepad"}' http://localhost:5000/text`
  - Áudio: Envie um arquivo WAV para `http://localhost:5000/audio`.

## Configuração

Edite `config/system_config.yaml` para ajustar modelos, URLs e comandos permitidos.

## Principais Funcionalidades

- 100% local, sem dependências pagas
- Suporte a GPU (CUDA) para modelos LLM e Whisper
- Plugins dinâmicos e expansíveis (ex: controle de mídia, clima)
- Frontend moderno (WebRTC, tema escuro, botão microfone)
- Suporte a múltiplos idiomas (voz/texto)
- TTS offline (pyttsx3) e fallback automático
- Integração LLaMA (llama.cpp via llama-cpp-python)
- Logging avançado e troubleshooting
- Testes automatizados para todos os módulos
- Documentação detalhada e exemplos de uso

## Exemplo de Configuração de Plugins

```yaml
plugins:
  media_control:
    enabled: true
  weather_plugin:
    enabled: true
    api_key: "SUA_API_KEY"
```

## Exemplo de Uso via CLI

```powershell
# Texto
Invoke-RestMethod -Uri http://localhost:5000/text -Method Post -Body (@{text='abrir notepad'} | ConvertTo-Json) -ContentType 'application/json'

# Áudio
Invoke-RestMethod -Uri http://localhost:5000/audio -Method Post -InFile .\audio.wav -ContentType 'audio/wav'
```

## Testes

Execute os testes com:
```bash
docker exec -it localjarvis_core_1 pytest tests/
```

## Contribuição

Veja `CONTRIBUTING.md` para diretrizes.

## Licença

MIT
