from sqlalchemy import Column, Float, String, Date, DateTime, Integer

from .database import Base

class CovidValue(Base):

    __tablename__ = "covid_values"

    id = Column(Integer, primary_key=True, index=True)
    province_state = Column(String)
    country_region = Column(String)
    lat            = Column(Float)
    lon            = Column(Float)
    date           = Column(Date)
    confirmed      = Column(Integer)
    deaths         = Column(Integer)
    recovered      = Column(Integer)
    created_at     = Column(DateTime)


