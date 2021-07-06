import csv
import codecs

from io import StringIO
from fastapi import FastAPI,  File, UploadFile
from fastapi.encoders import jsonable_encoder
from typing import Optional, List

from termstructure import *
from bonds import *
import faspy.nbutils.nbcurves as nbc

from numpy import datetime64 as dt64, datetime_as_string as datestr
from conventions import *
from helpers import *


myfreeapi = FastAPI()


@myfreeapi.get("/")
async def root():
    return {"message": "Hello World"}


@myfreeapi.post("/calc_curvedf/")
async def calc_curvedf(curve:TermStructure):

    thecurve = jsonable_encoder(curve)
    stset = thecurve['depo_settings']
    ltset = thecurve['lt_settings']
    strates = thecurve['depo_rates']
    ltrates = thecurve['lt_rates']
    
    stcurve = {}
    vdates = [dt64(thecurve['value_date'])]
    for strate in strates:
        stcurve[strate['tenor']] = strate['rate']
    
    ltcurve = {}
    for ltrate in ltrates:
        ltcurve[ltrate['tenor']] = ltrate['rate']               
    
    gen_df = nbc.generate_fulldf
    dfs = gen_df(vdates, [stcurve], stset['day_count'], stset['business_day'],
                    stset['rate_basis'], [ltcurve], ltset['day_count'],
                    ltset['business_day'], frequency=frequencies[ltset['frequency']],
                    method="Forward from issue date",
                    holidays=[])
    
    discountfactors = {"date": thecurve['value_date'], "termstructure": []}
    df = dfs[0]
    terms = list(map(lambda time, day, disfac: {"time":float(time), "day": int(day), "df": float(disfac)}, df['times'], df['days'], df['dfs'] ))
    
    return {"result": terms}


@myfreeapi.post("/calc_fixbond/")
async def calc_fixbond(bond:FixedRateBond):
    thebond = jsonable_encoder(bond)
    data = {"value_date":dt64(thebond['value_date']), "maturity": dt64(thebond['maturity']),
            "day_count": thebond['settings']['day_count'], "frequency":thebond['settings']['frequency'],
            "business_day": thebond['settings']['business_day'],
            "date_generation": thebond['settings']['date_generation'],
            "face_value": thebond['face_value'], "coupon": thebond['coupon'], 
            "ytm": thebond['ytm']}
    val = fixbond(data)
    for structure in val['structure']:
        structure['start_date'] = datestr(structure['start_date'])
        structure['end_date'] = datestr(structure['end_date'])
    return {"result": val}


@myfreeapi.post("/uploadfiles/")
async def uploadfiles(rate_set: UploadFile = File(...), 
                    rates: UploadFile = File(...),
                    pos_bond: Optional[UploadFile] = File(None),
                    pos_discount: Optional[UploadFile] = File(None),
                    pos_depo: Optional[UploadFile] = File(None),
                    holidays: Optional[UploadFile] = File(None)):

    #Processing csv files
    rateset = rateset_fromfile(rate_set.file)
    ratesall =  rates_fromfile(rates.file)
    #return ratesall
    calc_ts(ratesall, rateset, holidays=None)
    holi = None
    postbond = None
    if holidays:
        holi = holidays_fromfile(holidays.file)
    if pos_bond:
        postbond = postbond_fromfile(pos_bond.file)
        calc_bondstructures(postbond, holidays=holi)

    

    
    return ratesall
