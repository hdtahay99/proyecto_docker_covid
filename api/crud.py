from sqlalchemy.orm import Session
from sqlalchemy import and_
from sqlalchemy import func

from api.schemas import CovidValue
from datetime import date
from . import models


def get_covid_values(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.CovidValue).offset(skip).limit(limit).all()

def get_covid_filter(db: Session, skip: int = 0, limit: int = 100, status: str = 'Deaths'):
    return db.query(models.CovidValue).filter(models.CovidValue.status == status).offset(skip).limit(limit).all()

def get_data_covid_test(db: Session, date, status: str = 'Deaths'):
    return db.query(models.CovidValue).filter(models.CovidValue.date==date,
                                              models.CovidValue.status==status
                                              ).all()



def get_data_covid_test2(db: Session, date_from: date,date_to: date, status: str = 'Deaths'):
    return db.query(models.CovidValue).filter(and_(models.CovidValue.date >= date_from,
                                                   models.CovidValue.date <= date_to),
                                              models.CovidValue.status==status
                                              ).all()