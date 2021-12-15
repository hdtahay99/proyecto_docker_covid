from sqlalchemy.orm import Session
from sqlalchemy import and_

from datetime import date
from . import models


def get_covid_values(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.CovidValue).offset(skip).limit(limit).all()

def get_data_covid_test(db: Session, date):
    return db.query(models.CovidValue).filter(models.CovidValue.date==date).all()

def get_data_covid_test2(db: Session, date_from: date,date_to: date):
    return db.query(models.CovidValue).filter(and_(models.CovidValue.date >= date_from,
                                                   models.CovidValue.date <= date_to)).all()