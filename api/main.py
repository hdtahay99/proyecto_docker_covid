import pandas as pd

from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from . import crud, schemas
from .database import SessionLocal, engine

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/covid/values", response_model=List[schemas.CovidValue])
def read_covid_values(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    res = crud.get_covid_values(db, skip=skip, limit=limit)
    return res


@app.get("/covid/values/test1", response_model=List[schemas.CovidValue])
def read_data_covid_test(date: date, db: Session = Depends(get_db)):
    res = crud.get_data_covid_test(db, date=date)
    return res

@app.get("/covid/values/test2", response_model=List[schemas.CovidValue])
def read_data_covid_test2(date_from: date,date_to: date, db: Session = Depends(get_db)):
    res = crud.get_data_covid_test2(db, date_from=date_from,date_to=date_to)
    return res
