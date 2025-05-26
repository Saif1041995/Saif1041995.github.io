from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
import pandas as pd
from sqlalchemy import create_engine
import io
import random
from faker import Faker
from datetime import datetime, timedelta

app = FastAPI()
engine = create_engine("sqlite:///data.db")
fake = Faker()

# Initialize with 100 sample employee records
def init_db():
        pd.read_sql("SELECT * FROM employees", engine)

init_db()

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <h2>Employee Data API</h2>
    <p><a href="/data">View Employees</a></p>
    <p>Upload CSV with matching columns at <code>/upload</code></p>
    """

@app.get("/data")
def get_data():
    df = pd.read_sql("SELECT * FROM employees", engine)
    return df.to_dict(orient="records")

@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
    
    expected_cols = {"first_name", "last_name", "position", "salary", "start_date", "department"}
    if not expected_cols.issubset(set(df.columns)):
        return {"error": f"CSV must contain columns: {expected_cols}"}
    
    df.to_sql("employees", engine, index=False, if_exists="replace")
    return {"status": "uploaded", "rows": len(df)}
