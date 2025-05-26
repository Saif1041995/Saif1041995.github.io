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
    try:
        # Try reading to check if table exists
        pd.read_sql("SELECT * FROM employees", engine)
    except:
        data = {
            "first_name": [fake.first_name() for _ in range(100)],
            "last_name": [fake.last_name() for _ in range(100)],
            "position": [random.choice(["Engineer", "Manager", "Analyst", "Clerk", "HR"]) for _ in range(100)],
            "salary": [round(random.uniform(30000, 120000), 2) for _ in range(100)],
            "start_date": [fake.date_between(start_date='-5y', end_date='today') for _ in range(100)],
            "department": [random.choice(["IT", "Finance", "HR", "Marketing", "Operations"]) for _ in range(100)],
        }
        df = pd.DataFrame(data)
        df.to_sql("employees", engine, index=False, if_exists="replace")

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
