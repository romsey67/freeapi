from fastapi import  UploadFile
import csv, codecs
from numpy import datetime64 as dt64, datetime_as_string as datestr
from faspy.interestrate.fixincome import fixbond_structures, fixbond_value, \
    date_structures, fixbond
from faspy.nbutils.nbcurves import generate_fulldf as gen_df
from conventions import *


def generaldata_fromfile(thefile):
    csv_data = csv.reader(codecs.iterdecode(thefile,  'utf-8'), delimiter=',')
    counter = 0
    coldict = {}
    data = []

    for row in csv_data:
        thedict = {}
        colno= len(row)
        if counter == 0:
            for i in range(colno):
                coldict[i] = row[i]
        else:
            for i in range(colno):
                if row[i] == '':
                    thedict[coldict[i]] = None
                else:
                    thedict[coldict[i]] = row[i]
            data.append(thedict)
        counter +=1
    
    return data


def rateset_fromfile(thefile):
    all_set = generaldata_fromfile(thefile)
    ccy_list = set([x['ccy'] for x in all_set])
    #all_ccy_rates = []
    
    for x in ccy_list:
        ccy_rates = {}
        #copy dictionary for the currency
        curvebyccy = [data.copy() for data in all_set if data['ccy'] == x]
        ccy_rates[x] = {}
        
        for curve in curvebyccy:
            curve.pop('ccy')
            ccy_rates[x][curve['curvename']] = curve
            curve.pop('curvename')

        #all_ccy_rates.append(ccy_rates)
        
    return ccy_rates #all_ccy_rates


def rates_fromfile(thefile):

    rates = generaldata_fromfile(thefile)
    ccy_list = set([x['ccy'] for x in rates])
    #all_ccy_rates = []
    
    for x in ccy_list:
        ccy_rates = {}
        #copy dictionary for the currency
        curvebyccy = [data.copy() for data in rates if data['ccy'] == x]
        ccy_rates[x] = {}
        
        for curve in curvebyccy:
            curvename = curve['curvename']
            if ccy_rates[x].get(curvename):
                curve.pop('ccy')
                curve.pop('curvename')
                ccy_rates[x][curvename].append(curve)
            else:
                ccy_rates[x][curvename] = []
                curve.pop('ccy')
                curve.pop('curvename')
                ccy_rates[x][curvename].append(curve)
            
        #all_ccy_rates.append(ccy_rates)
    
    return ccy_rates #all_ccy_rates


def postbond_fromfile(thefile):
    positions = generaldata_fromfile(thefile)
    date_list = set([x['position_date'] for x in positions])
    bondexp = {}
    for adate in date_list:
        posbydate = [data.copy() for data in positions if data['position_date'] == adate]
        bondexp[adate] = {}
        ccy_list = set([x['ccy'] for x in posbydate])
        for ccy in ccy_list:
            posbydatenccy = [data.copy() for data in posbydate if data['ccy'] == ccy]
            anexp = bondexp[adate]
            for pos in posbydatenccy:
                if anexp.get(ccy):
                    anexp.get(ccy).append(pos)
                else:
                    anexp[ccy] = []
                    anexp.get(ccy).append(pos)
    
    return bondexp


def holidays_fromfile(thefile):
    holidays = generaldata_fromfile(thefile)
    ccy_list = set([x['ccy'] for x in holidays])
    holi = {}
    for ccy in ccy_list:
        holibyccy = [x['date'] for x in holidays if x['ccy'] == ccy]
        holi[ccy] = holibyccy
    return holi


def calc_bondstructures(thebonds, holidays=None):
    # thebonds is in the following format
    # { actualdate: {actual ccy: [data] }}

    for adate in thebonds.keys():
        value_date = dt64(adate)
        bondbydate = thebonds[adate]
        for accy in bondbydate.keys():
            bondbyccy = bondbydate[accy]
            for bond in bondbyccy:
                bondinfo = {"value_date":value_date, "maturity": dt64(bond['maturity']),
                    "day_count": bond['day_count'], "frequency":bond['frequency'],
                    "business_day": bond['business_day'],
                    "date_generation": bond['date_generation_basis'],
                    "face_value": float(bond['face_value']), "coupon": float(bond['coupon']), 
                    "ytm": None}
                val = list(fixbond_structures(bondinfo))
                for ea in val:
                    ea['start_date'] = datestr(ea['start_date'])
                    ea['end_date'] = datestr(ea['end_date'])
                bond['structure'] = val
    return


def calc_ts(ts_rates, ts_setting, holidays=None):
    counter = 0
    for ccy in ts_rates.keys():
        ccy_rates = ts_rates[ccy]
        holi = []
        if holidays is not None:
            if holidays[ccy]:
                holi = holidays[ccy]
                holi = [dt64(x) for x in holi]

        for curvename in ccy_rates.keys():
            ts = ccy_rates[curvename]
            #print(ts_setting)
            ts_set = ts_setting[ccy][curvename]

            #ts is an error
            #going through each curve in the array
            for ats in ts:
                vdate = dt64(ats["date"])
                #preparing the depo rates
                stcurve = {}
                for tenor in st_tenors:
                    if ats.get(tenor):
                        stcurve[tenor] = float(ats[tenor])

                #preparing the lt rates
                ltcurve = {}
                for tenor in lt_tenors:
                    if ats.get(tenor):
                        ltcurve[tenor] = float(ats[tenor])
                
                #print(ts_set, stcurve, ltcurve)
                #print('==============================================')
                dfs = gen_df([vdate], [stcurve], ts_set['depo_daycount'], 
                            ts_set['depo_businessday'], ts_set['depo_ratebasis'],
                            [ltcurve], ts_set['lt_daycount'], ts_set['depo_businessday'], 
                            frequency=frequencies[ts_set['lt_frequency']],
                            method=ts_set['lt_dategeneration'],
                            holidays=holi)
                df = dfs[0]
                terms = list(map(lambda time, day, disfac: {"time":float(time), "day": int(day), "df": float(disfac)}, df['times'], df['days'], df['dfs'] ))
                ats['dfs'] = terms
                counter += 1
                print(counter)
                    










    

                    








