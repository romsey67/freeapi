import csv
import codecs
import json

from io import StringIO
from fastapi import FastAPI,  File, UploadFile, Form, Body
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


@myfreeapi.post("/calc_dffromfiles/")
async def uploadfiles(rate_set: UploadFile = File(...), 
                    rates: UploadFile = File(...),
                    holidays: Optional[UploadFile] = File(None)):

    #Processing csv files
    rateset = rateset_fromfile(rate_set.file)
    ratesall =  rates_fromfile(rates.file)
    #return ratesall
    # calc_ts(ratesall, rateset, holidays=None)
    discountfactors = calc_disountfactors(rateset, ratesall, 
                        allholidays=None)
    #holi = None
    #postbond = None
    #if holidays:
    #    holi = holidays_fromfile(holidays.file)
    #if pos_bond:
    #    postbond = postbond_fromfile(pos_bond.file)
    #    calc_bondstructures(postbond, holidays=holi)
    
    return discountfactors


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


@myfreeapi.get("/header_rate_set/")
async def header_rate_set():
    return {'header':['ccy', 'curvename', 'depo_ratebasis', 'depo_businessday',
        'depo_daycount', 'lt_frequency', 'lt_businessday', 'lt_daycount', 
        'lt_dategeneration']}


@myfreeapi.get("/header_historical_rates/")
async def header_historical_rates():
    return {'header':['date', 'ccy', 'curvename', 'O/N','1W', '2W', '3W', '1M', 
            '2M','3M', '4M', '5M', '6M', '12M', '1Y', '2Y', '3Y', '4Y', '5Y','7Y',
            '10Y', '15Y', '20Y', '30Y']}


@myfreeapi.get("/header_position_bonds/")
async def header_position_bonds():
    return {'header':['position_date', 'id', 'face_value', 'curvename','ccy', 
            'issuer', 'issue_date', 'day_count', 'business_day','frequency', 
            'coupon', 'maturity', 'date_generation_basis']}



@myfreeapi.post("/convert_holidays/")
async def convert_holidays(holidays: UploadFile = File(...)):
    holi = holidays_fromfile(holidays.file)
    return holi


@myfreeapi.post("/convert_ratesetting/")
async def convert_ratesetting(rate_set: UploadFile = File(...)):
    rateset = rateset_fromfile(rate_set.file)
    return rateset


@myfreeapi.post("/convert_rates/")
async def convert_rates(rates: UploadFile = File(...)):
    ratesall =  rates_fromfile(rates.file)
    return ratesall


# TO DO
@myfreeapi.post("/convert_rates2/")
async def convert_rates2(rate_set: str = Body(...), rates: UploadFile = File(...)):
    #ratesall =  rates_fromfile(rates.file)
    data = json.loads(rate_set)
    return data


