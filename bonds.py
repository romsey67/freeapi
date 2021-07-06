from typing import Optional, List
from pydantic import BaseModel
from enums import *


class CouponStructure(BaseModel):
    face_value: float
    start_date: str
    end_date: str
    coupon: float
    interest: float
    fv_flow: float
    

class SettingBond(BaseModel):
    frequency: Optional[Frequency] = "Semi-Annual"
    business_day: Optional[BusinessDay]= "Modified Following"
    day_count: Optional[DayCount] = "Actual/365"
    date_generation: Optional[DateGeneration] = "Backward from maturity date"


class FixedRateBond(BaseModel):
    value_date: str
    settings: Optional[SettingBond]
    face_value: float
    issue_date: Optional[str] = None
    maturity: str
    coupon: float = 0.00
    ytm: Optional[float] = None
    structures: Optional[List[CouponStructure]] = None
    curve: Optional[str]


