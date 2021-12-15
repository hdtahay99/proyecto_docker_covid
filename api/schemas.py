from typing import List, Optional
from datetime import date
from pydantic import BaseModel


class CovidValueBase(BaseModel):
    province_state : str 
    country_region : str
    lat            : float
    lon            : float
    date           : date
    confirmed      : int
    deaths         : int
    recovered      : int





class CovidValueCreate(CovidValueBase):
    pass



class CovidValue(CovidValueBase):
    
    class Config:
        orm_mode = True
