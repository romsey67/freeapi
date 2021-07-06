from typing import Optional, List
from fastapi import  UploadFile
from pydantic import BaseModel
from enums import *


class SettingDepo(BaseModel):
    rate_basis: Optional[RateBasis] = "Simple"
    business_day : Optional[BusinessDay]= "Modified Following"
    day_count: Optional[DayCount] = "Actual/365"


class TSDepoPoint(BaseModel):
    tenor: DepoTenors
    rate: Optional[float] = None

    

class SettingLT(BaseModel):
    frequency: Optional[Frequency] = "Semi-Annual"
    business_day : Optional[BusinessDay]= "Modified Following"
    day_count: Optional[DayCount] = "Actual/365"


class TSLTPoint(BaseModel):
    tenor: LTTenors
    rate: Optional[float] = None

class RatesLT(BaseModel):
    rates: List[TSLTPoint]


class TermStructure(BaseModel):
    value_date: str
    depo_settings: SettingDepo
    depo_rates: List[TSDepoPoint]
    lt_settings: SettingLT
    lt_rates: List[TSLTPoint]

class TermStructures(BaseModel):
    ts: List[TermStructure]



class Holiday(BaseModel):
    ccy: str
    dates: List[str]

class Holidays(BaseModel):
    holi: Optional[List[Holiday]] = None

    

