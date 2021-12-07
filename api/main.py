import pandas as pd

from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine


#models.Base.metadata.create_all(bind=engine)

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
    return {"Hello": "Changes"}

@app.get("/covid/values", response_model=List[schemas.CovidValue])
def read_covid_values(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    res = crud.get_covid_values(db, skip=skip, limit=limit)
    return res


@app.get("/covid/values/filter", response_model=List[schemas.CovidValue])
def read_covid_values(skip: int = 0, limit: int = 100, status: str = 'Deaths', db: Session = Depends(get_db)):
    res = crud.get_covid_filter(db, skip=skip, limit=limit, status=status)
    return res
