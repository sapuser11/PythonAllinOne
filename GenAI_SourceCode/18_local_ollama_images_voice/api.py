from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import shutil
from pathlib import Path
from model_processor import process_image, process_audio, chat_with_text

app = FastAPI()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/process-image")
async def process_image_endpoint(file: UploadFile = File(...)):
    """Process uploaded image"""
    file_path = UPLOAD_DIR / file.filename
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    result = process_image(str(file_path))
    file_path.unlink()  # Clean up
    
    return JSONResponse(content={"result": result})

@app.post("/process-audio")
async def process_audio_endpoint(file: UploadFile = File(...)):
    """Process uploaded audio"""
    file_path = UPLOAD_DIR / file.filename
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    result = process_audio(str(file_path))
    file_path.unlink()  # Clean up
    
    return JSONResponse(content=result)

@app.post("/chat")
async def chat_endpoint(text: str):
    """Process text chat"""
    result = chat_with_text(text)
    return JSONResponse(content={"response": result})

@app.get("/")
async def root():
    return {"message": "Ollama API is running"}