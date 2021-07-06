from typing import Optional, List
from pydantic import BaseModel
from enums import *
from termstructure import *
from bonds import *

class Exposure(BaseModel):
    fixbond: List[FixedRateBond]
