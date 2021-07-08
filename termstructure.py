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


class RateSetting(BaseModel):
    curvename: str
    depo_ratebasis: Optional[RateBasis] = "Simple"
    depo_businessday : Optional[BusinessDay]= "Modified Following"
    depo_daycount: Optional[DayCount] = "Actual/365"
    lt_frequency: Optional[Frequency] = "Semi-Annual"
    lt_businessday : Optional[BusinessDay]= "Modified Following"
    lt_daycount: Optional[DayCount] = "Actual/365"
    lt_dategeneration: Optional[DateGeneration] = "Backward from maturity date"


class RateSettings(BaseModel):
    ccy: str 
    settings: List[Optional[RateSetting]] = []


class AllRateSettings(BaseModel):
    irsettings: List[Optional[RateSettings]] = []


class Curve(BaseModel):
    date: str 
    o_n: Optional[float]
    w1: Optional[float]
    w1: Optional[float]
    w3: Optional[float]
    m1: Optional[float]
    m3: Optional[float]
    m4: Optional[float]
    m5: Optional[float]
    m6: Optional[float]
    m9: Optional[float]
    m12: Optional[float]
    y1: Optional[float]
    y2: Optional[float]
    y3: Optional[float]
    y4: Optional[float]
    y5: Optional[float]
    y7: Optional[float]
    y10: Optional[float]
    y15: Optional[float]
    y20: Optional[float]
    y30: Optional[float]


class IRCurve(BaseModel):
    curvename: str
    rates: List[Optional[Curve]] = []


class IRCurves(BaseModel):
    ccy: str
    curves: List[Optional[IRCurve]] = []


class AllIRCurves(BaseModel):
    curves: List[Optional[IRCurves]] = []


class DiscountCurve(BaseModel):
    date: str
    times: List[float]
    days: List[int]
    df: List[float]


class HistoricalDiscountCurve(BaseModel):
    curvename: str 
    curves: List[Optional[DiscountCurve]] = []


class DiscountCurves(BaseModel):
    ccy: str 
    curves: List[Optional[HistoricalDiscountCurve]] = []

class AllDiscountCurves(BaseModel):
    curves: List[Optional[DiscountCurves]] = []

class CcyHolidays(BaseModel):
    ccy: str 
    dates: List[Optional[str]] = []


class AllHolidays(BaseModel):
    holidays: List[Optional[CcyHolidays]] = []


