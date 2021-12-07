from sqlalchemy.orm import Session

from api.schemas import CovidValue

from . import models


def get_covid_values(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.CovidValue).offset(skip).limit(limit).all()

def get_covid_filter(db: Session, skip: int = 0, limit: int = 100, status: str = 'Deaths'):
    return db.query(models.CovidValue).filter(models.CovidValue.status == status).offset(skip).limit(limit).all()

