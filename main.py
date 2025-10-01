from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import List
import pandas as pd
import io
import os

app = FastAPI()

# Load db2.xlsx if exists
db2 = pd.DataFrame()
if os.path.exists("data_uploaded.xlsx"):
    db2 = pd.read_excel("data_uploaded.xlsx")

# Load employees.csv if exists
CSV_PATH = "db.xlsx"
employee_df = pd.read_excel(CSV_PATH)

# JSON schema for employee
class Employee(BaseModel):
    set_id: int
    name: str
    year: int
    theme: str
    subtheme: str
    themeGroup: str
    category: str
    pieces: float	
    minifigs: float	
    agerange_min: float	
    US_retailPrice: float	
    bricksetURL	: str
    thumbnailURL: str
    imageURL : str
    
@app.get("/")
def read_root():
    return {"message": "Welcome to the data transfer API"}

@app.get("/db")
def get_employees():
    return employee_df.to_dict(orient="records")

@app.get("/db2")
def get_db2():
    return db2.to_dict(orient="records")

@app.post("/upload_data")
async def upload_csv(file: UploadFile = File(...)):
    global employee_df
    content = await file.read()
    df = pd.read_csv(io.StringIO(content.decode("utf-8")))
    employee_df = pd.concat([employee_df, df], ignore_index=True)
    return {"status": "success", "rows_added": len(df), "total_rows": len(employee_df)}
