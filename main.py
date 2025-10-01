# main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import pandas as pd
import os

app = FastAPI(title="Excel Transfer API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_headers=["*"], allow_methods=["*"]
)

DATA_DIR = Path("data"); DATA_DIR.mkdir(exist_ok=True)

def safe(n: str) -> str: return os.path.basename(n)

@app.get("/health")
def health(): return {"status": "ok"}

@app.post("/upload")
async def upload_excel(file: UploadFile = File(...)):
    name = safe(file.filename)
    if not name.lower().endswith((".xlsx", ".xls")):
        raise HTTPException(400, "Upload .xlsx or .xls")
    dest = DATA_DIR / name
    with dest.open("wb") as f: f.write(await file.read())
    return {"ok": True, "filename": name}

@app.get("/download/{filename}")
def download(filename: str):
    p = DATA_DIR / safe(filename)
    if not p.exists(): raise HTTPException(404, "Not found")
    return FileResponse(p, filename=p.name)

@app.get("/excel/{filename}/json")
def to_json(filename: str, sheet: int | str | None = None, nrows: int | None = None):
    p = DATA_DIR / safe(filename)
    if not p.exists(): raise HTTPException(404, "Not found")
    df = pd.read_excel(p, sheet_name=sheet if sheet is not None else 0, nrows=nrows)
    return JSONResponse(df.to_dict(orient="records"))
