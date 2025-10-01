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
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"],
)

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = Path("db.xlsx")

def safe(n: str) -> str:
    # prevent path traversal
    return os.path.basename(n)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/get_db")
def get_db():
    if not DB_PATH.exists():
        raise HTTPException(status_code=404, detail="db.xlsx not found")
    try:
        df = pd.read_excel(DB_PATH)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed reading db.xlsx: {e!s}")
    # FastAPI will JSON-serialize lists/dicts automatically
    return df.to_dict(orient="records")

@app.post("/upload")
async def upload_excel(file: UploadFile = File(...)):
    name = safe(file.filename or "")
    if not name.lower().endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Upload .xlsx or .xls")

    dest = DATA_DIR / name
    try:
        with dest.open("wb") as f:
            # stream in chunks to avoid loading whole file into memory
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                f.write(chunk)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e!s}")
    finally:
        await file.close()

    return {"ok": True, "filename": name}

@app.get("/download/{filename}")
def download(filename: str):
    p = DATA_DIR / safe(filename)
    if not p.exists():
        raise HTTPException(status_code=404, detail="Not found")
    return FileResponse(p, filename=p.name)

@app.get("/excel/{filename}/json")
def to_json(
    filename: str,
    sheet: int | str | None = None,
    nrows: int | None = None,
):
    p = DATA_DIR / safe(filename)
    if not p.exists():
        raise HTTPException(status_code=404, detail="Not found")
    try:
        df = pd.read_excel(
            p,
            sheet_name=(sheet if sheet is not None else 0),
            nrows=nrows,
        )
    except ValueError as e:
        # e.g., sheet name/index errors
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed reading Excel: {e!s}")

    # If the sheet is a Series (single column), normalize to DataFrame
    if hasattr(df, "to_dict"):
        data = df.to_dict(orient="records")
    else:
        # pandas may return a dict of DataFrames for multiple sheets (unlikely here, but safe)
        raise HTTPException(status_code=400, detail="Expected a single sheet")

    return JSONResponse(content=data)
