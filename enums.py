
from enum import Enum

class BusinessDay(str, Enum):
    no_adj = "No Adjustment"
    mod_fol = "Modified Following"
    fol = "Following"


class DayCount(str, Enum):
    a365 = "Actual/365"
    a365F = "Actual/365 Fixed"
    act_act = "Actual/Actual"


class Frequency(str, Enum):
    annual = "Annual"
    semi_annual = "Semi-Annual"
    quarterly = "Quarterly"


class RateBasis(str, Enum):
    simple = "Simple"
    discount = "Discount Rate"
    continuous = "Continuous"


class DepoTenors(str, Enum):
    week1 = "1W"
    week2 = "2W"
    week3 = "3W"
    month1 = "1M"
    month2 = "2M"
    month3 = "3M"
    month4 = "4M"
    month5 = "5M"
    month6 = "6M"
    month9 = "9M"
    month12 = "12M"


class LTTenors(str, Enum):
    year1 = "1Y"
    year2 = "2Y"
    year3 = "3Y"
    year4 = "4Y"
    year5 = "5Y"
    year6 = "6Y"
    year7 = "7Y"
    year10 = "10Y"
    year15 = "15Y"
    year20 = "20Y"
    year30 = "30Y"


class DateGeneration(str, Enum):
    forward = "Forward from issue date"
    backward = "Backward from maturity date"

