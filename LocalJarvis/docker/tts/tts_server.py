from fastapi import FastAPI, Request
from gtts import gTTS
import io
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.post("/synthesize")
async def synthesize(request: Request):
    try:
        data = await request.json()
        text = data["text"]
        tts = gTTS(text)
        buffer = io.BytesIO()
        tts.write_to_fp(buffer)
        logger.info("Síntese de áudio concluída.")
        return buffer.getvalue()
    except Exception as e:
        logger.error(f"Erro na síntese: {e}")
        raise
