# LocalJarvis

Um assistente virtual local, inspirado no Jarvis do Homem de Ferro, que processa comandos de voz ou texto, executa ações no sistema e mantém histórico conversacional. Tudo roda em Docker, sem APIs pagas.

## 🚀 Quickstart

1. Pré-requisitos:
   - Docker 20.10+
   - (Opcional) Nvidia Container Toolkit para GPU

2. Inicialização:
   ```powershell
   git clone <URL_DO_REPOSITORIO>
   cd LocalJarvis
   cp .env.example .env  # Configure as variáveis
   docker-compose up --build
   ```

3. Testes:
   ```powershell
   # Testes unitários
   docker-compose exec core pytest tests/

   # Verificação de serviços
   ./scripts/healthcheck.sh
   ```

## 🔧 Configuração
| Variável            | Default               | Descrição                |
|---------------------|-----------------------|--------------------------|
| TTS_SERVICE_URL     | http://tts:5002       | URL do serviço TTS       |
| STT_SERVICE_URL     | http://whisper:5001   | URL do serviço STT       |
| LOG_LEVEL           | INFO                  | DEBUG\|INFO\|WARNING\|ERROR |

## Uso

- **Web**: Acesse `http://localhost:5000` e use o chat.
- **API**:
  - Texto: `curl -X POST -H "Content-Type: application/json" -d '{"text":"abrir notepad"}' http://localhost:5000/text`
  - Áudio: Envie um arquivo WAV para `http://localhost:5000/audio`.

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
```powershell
docker-compose exec core pytest tests/
```

## Healthcheck dos Serviços

Execute para validar endpoints principais:
```powershell
bash ./scripts/healthcheck.sh
```

## Logging

Os logs ficam disponíveis em `/app/logs/jarvis.log` dentro do container core.

## Boas Práticas

- Versione imagens: `docker build -t jarvis-core:$(git rev-parse --short HEAD) -f docker/core/Dockerfile .`
- Use CI/CD para build/teste automático.
- Monitore logs em tempo real: `docker-compose logs -f --tail=100 --no-color | tee combined.log`

## Contribuição

Veja `CONTRIBUTING.md` para diretrizes.

## Licença

MIT
