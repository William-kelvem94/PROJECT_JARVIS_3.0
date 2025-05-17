from fastapi import FastAPI, UploadFile
import whisper
import logging
import tempfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
