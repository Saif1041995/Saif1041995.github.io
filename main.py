from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import List
import pandas as pd
import io
import os

app = FastAPI()

# Load db2.xlsx if exists
db2 = pd.DataFrame()
if os.path.exists("db2.xlsx"):
    db2 = pd.read_excel("db2.xlsx")

# Load employees.csv if exists
CSV_PATH = "employees.csv"
employee_df = pd.DataFrame()
if os.path.exists(CSV_PATH):
    employee_df = pd.read_csv(CSV_PATH)
else:
    # Fallback: Generate sample data
    employee_df = pd.DataFrame([
        {
            "first_name": f"First{i}",
            "last_name": f"Last{i}",
            "position": "Engineer",
            "salary": 5000 + i * 10,
            "start_date": f"2020-01-{(i % 30) + 1:02d}",
            "department": "R&D"
        } for i in range(1, 101)
    ])

# JSON schema for employee
class Employee(BaseModel):
    first_name: str
    last_name: str
    position: str
    salary: float
    start_date: str
    department: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the Employee API"}

@app.get("/employees")
def get_employees():
    return employee_df.to_dict(orient="records")

@app.get("/db2")
def get_db2():
    return db2.to_dict(orient="records")

@app.post("/upload_json")
def upload_json(data: List[Employee]):
    global employee_df
    new_df = pd.DataFrame([d.dict() for d in data])
    employee_df = pd.concat([employee_df, new_df], ignore_index=True)
    return {"status": "success", "rows_added": len(new_df), "total_rows": len(employee_df)}

@app.post("/upload_csv")
async def upload_csv(file: UploadFile = File(...)):
    global employee_df
    content = await file.read()
    df = pd.read_csv(io.StringIO(content.decode("utf-8")))
    employee_df = pd.concat([employee_df, df], ignore_index=True)
    return {"status": "success", "rows_added": len(df), "total_rows": len(employee_df)}
