from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import List
import pandas as pd
import io

app = FastAPI()

# In-memory DataFrame
employee_df = pd.DataFrame(columns=["first_name", "last_name", "position", "salary", "start_date", "department"])

# Sample Data Generator (optional)
def generate_sample_data():
    global employee_df
    employee_df = pd.DataFrame([
        {
            "first_name": f"First{i}",
            "last_name": f"Last{i}",
            "position": "Engineer",
            "salary": 5000 + i * 10,
            "start_date": f"2020-01-{(i%30)+1:02d}",
            "department": "R&D"
        } for i in range(1, 101)
    ])

generate_sample_data()

# JSON Upload Endpoint
class Employee(BaseModel):
    first_name: str
    last_name: str
    position: str
    salary: float
    start_date: str  # Could be validated as date
    department: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the Employee API"}

@app.post("/upload_json")
def upload_json(data: List[Employee]):
    global employee_df
    new_df = pd.DataFrame([d.dict() for d in data])
    employee_df = pd.concat([employee_df, new_df], ignore_index=True)
    return {"status": "success", "rows_added": len(new_df), "total_rows": len(employee_df)}

# CSV Upload Endpoint
@app.post("/upload_csv")
async def upload_csv(file: UploadFile = File(...)):
    global employee_df
    content = await file.read()
    df = pd.read_csv(io.StringIO(content.decode("utf-8")))
    employee_df = pd.concat([employee_df, df], ignore_index=True)
    return {"status": "success", "rows_added": len(df), "total_rows": len(employee_df)}

# Read all employees
@app.get("/employees")
def get_employees():
    return employee_df.to_dict(orient="records")


@app.get("/employees_df")
def get_employees_df():
    return employee_df
