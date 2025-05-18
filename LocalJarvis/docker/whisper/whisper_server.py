from fastapi import FastAPI, UploadFile
import whisper
import logging
import tempfile
try:
    import multipart
except ImportError:
    logging.warning("python-multipart não está instalado! Uploads multipart podem falhar.")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Servidor Whisper iniciado com sucesso.")

app = FastAPI()
model = whisper.load_model("base")

@app.post("/transcribe")
async def transcribe(file: UploadFile):
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_file.write(await file.read())
            temp_file_path = temp_file.name
        result = model.transcribe(temp_file_path)
        logger.info("Transcrição concluída.")
        return {"text": result["text"]}
    except Exception as e:
        logger.error(f"Erro na transcrição: {e}")
        raise
