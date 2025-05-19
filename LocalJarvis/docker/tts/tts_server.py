from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from gtts import gTTS
import io
import logging
import yaml
import os
import psutil
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar configuração centralizada
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '../../config/system_config.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

config = load_config()

def get_cpu_info():
    return {
        'cpu_percent': psutil.cpu_percent(),
        'memory_percent': psutil.virtual_memory().percent
    }

app = FastAPI()

# Instanciação única do modelo (gTTS é stateless, mas pode ser adaptado para outros modelos)

@app.post("/synthesize")
async def synthesize(request: Request):
    try:
        data = await request.json()
        text = data.get("text", "").strip()
        if not text:
            logger.warning("Texto vazio recebido para síntese.")
            return JSONResponse(status_code=HTTP_400_BAD_REQUEST, content={"error": "Campo 'text' é obrigatório e não pode ser vazio."})
        tts = gTTS(text, lang=config['tts'].get('voice', 'pt'))
        buffer = io.BytesIO()
        tts.write_to_fp(buffer)
        buffer.seek(0)
        logger.info(f"Síntese concluída para texto de {len(text)} caracteres.")
        return StreamingResponse(buffer, media_type="audio/mpeg")
    except Exception as e:
        logger.exception(f"Erro na síntese: {e}")
        return JSONResponse(status_code=HTTP_500_INTERNAL_SERVER_ERROR, content={"error": str(e)})

@app.get("/health")
def health():
    cpu_info = get_cpu_info()
    return {
        "status": "ok",
        "cpu": cpu_info,
        "tts_config": config['tts']
    }

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    logger.error(f"Erro de validação: {exc}")
    return JSONResponse(status_code=HTTP_400_BAD_REQUEST, content={"error": str(exc)})
