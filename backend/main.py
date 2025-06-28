from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from PIL import Image
from pyzbar.pyzbar import decode

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    filepath = os.path.join(UPLOAD_DIR, file.filename)
    with open(filepath, "wb") as f:
        f.write(await file.read())
    return {"message": "File uploaded", "filename": file.filename}

@app.get("/files")
async def list_files():
    files = os.listdir(UPLOAD_DIR)
    return {"files": files}

@app.get("/file/{filename}")
async def get_file(filename: str):
    filepath = os.path.join(UPLOAD_DIR, filename)
    return FileResponse(filepath)

@app.get("/extract_qr/{filename}")
async def extract_qr(filename: str):
    filepath = os.path.join(UPLOAD_DIR, filename)
    try:
        img = Image.open(filepath)
        decoded = decode(img)
        qr_data = [d.data.decode("utf-8") for d in decoded]
        return {"qr_data": qr_data}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})