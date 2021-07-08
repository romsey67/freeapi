
from fastapi.encoders import jsonable_encoder
import csv, codecs
from numpy import datetime64 as dt64, datetime_as_string as datestr
from faspy.interestrate.fixincome import fixbond_structures, fixbond_value, \
    date_structures, fixbond
from faspy.nbutils.nbcurves import generate_fulldf as gen_df
from conventions import *
from termstructure import *


def generaldata_fromfile(thefile, datatype=None):
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
            if datatype == "curve":
                for i in range(colno):
                    if tenors.get(coldict[i]):
                        coldict[i] = tenors[coldict[i]]
        else:
            for i in range(colno):
                if row[i] == '':
                    thedict[coldict[i]] = None
                else:
                    if datatype == 'curve':
                        if tenors_invs.get(coldict[i]):
                            thedict[coldict[i]] = float(row[i])
                        else:
                            thedict[coldict[i]] = row[i]
                    else:
                        thedict[coldict[i]] = row[i]
            data.append(thedict)
        counter +=1
    
    return data


def oldrateset_fromfile(thefile):
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


def rateset_fromfile(thefile):

    all_set = generaldata_fromfile(thefile)
    ccy_list = set([x['ccy'] for x in all_set])
    allsets = AllRateSettings()

    for ccy in ccy_list:
        thedict = {'ccy': ccy}
        ccysets = RateSettings(**thedict)
        #copy dictionary for the currency
        curvebyccy = [data for data in all_set if data['ccy'] == ccy]
        
        for curve in curvebyccy:
            theset = {"curvename": curve['curvename'], 'depo_ratebasis': curve['depo_ratebasis'], 
                    'depo_businessday' : curve['depo_businessday'], 'depo_daycount': curve['depo_daycount'],
                    'lt_frequency': curve['lt_frequency'], 'lt_businessday' : curve['lt_businessday'],
                    'lt_daycount': curve['lt_daycount'], 'lt_dategeneration': curve['lt_dategeneration']}
            ccyset = RateSetting(**theset)
            ccysets.settings.append(ccyset)
        allsets.irsettings.append(ccysets)
        
    return allsets 


def oldrates_fromfile(thefile):

    rates = generaldata_fromfile(thefile)
    ccy_list = set([x['ccy'] for x in rates])
    #all_ccy_rates = []
    
    for ccy in ccy_list:
        

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


def rates_fromfile(thefile):
    
    rates = generaldata_fromfile(thefile, datatype='curve')
    ccy_list = set([x['ccy'] for x in rates])
    allircurves = AllIRCurves()

    for ccy in ccy_list:
        theccy = {"ccy": ccy}    
        ircurves = IRCurves(**theccy)
        curvebyccy = [data for data in rates if data['ccy'] == ccy]
        namelist = set([x['curvename'] for x in rates])
        
        for curvename in namelist: 
            #print(curvebyccy)
            curvebyname = [data.copy() for data in curvebyccy if data['curvename'] == curvename]
            thename = {'curvename': curvename}
            ircurve = IRCurve(**thename)
            
            for curve in curvebyname:
                curve.pop('ccy')
                curve.pop('curvename')
            
            ircurve.rates=curvebyname
            ircurves.curves.append(ircurve)
        allircurves.allircurves.append(ircurves)
            
    return allircurves


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
    holidict = generaldata_fromfile(thefile)
    ccy_list = set([x['ccy'] for x in holidict])
    holidays = AllHolidays()
    #print(ccy_list)
    for ccy in ccy_list:
        thedict = {'ccy': ccy}
        holi = CcyHolidays(**thedict)
        holibyccy = [x['date'] for x in holidict if x['ccy']==ccy]
        holi.dates.append(holibyccy)
        holidays.holidays.append(holi)
    
    return holidays


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
                
                    

def calc_disountfactors(ratesettings: AllRateSettings, allirrates: AllIRCurves, 
                        allholidays: Holidays=None):
        
    settings = jsonable_encoder(ratesettings)
    settings = settings['irsettings']
    alldiscountcurves = AllDiscountCurves()
    #return allirrates.curves
    for curvesbyccy in allirrates.allircurves:
        ccy = curvesbyccy.ccy
        theccy = {'ccy': ccy}
        settsbyccy = list(filter(lambda x: x['ccy'] == ccy, settings))
        settsbyccy = settsbyccy[0]['settings']
        discountcurves = DiscountCurves(**theccy)
        
        for curvebyname in curvesbyccy.curves:
            curvename = curvebyname.curvename
            thecurvename = {'curvename': curvename}
            historicaldiscountcurve = HistoricalDiscountCurve(**thecurvename)
            settsbycurve = [setts for setts in settsbyccy if setts['curvename'] == curvename]
            
            if settsbycurve:
                setting = settsbycurve[0]
                vdates = []
                stcurves = []
                ltcurves = []

                for curve in curvebyname.rates:
                    vdates.append(dt64(curve['date']))
                    stcurve ={}
                    
                    for tenor, value in curve.items():
                        if value is not None:
                            if tenor in depotenors_invs.keys():
                                stcurve[depotenors_invs[tenor]] = value
                    stcurves.append(stcurve)
                    ltcurve ={}
                    for tenor, value in curve.items():
                        if value is not None:
                            if tenor in lttenors_invs.keys():
                                ltcurve[lttenors_invs[tenor]] = value
                    ltcurves.append(ltcurve)
                
                dfs = gen_df(vdates, stcurves, setting['depo_daycount'], 
                        setting['depo_businessday'], setting['depo_ratebasis'],
                        ltcurves, setting['lt_daycount'], setting['depo_businessday'], 
                        frequency=frequencies[setting['lt_frequency']],
                        method=setting['lt_dategeneration'],
                        holidays=[])
                datecount = len(vdates)
                dfs = list(dfs)
                for i in range(datecount):
                    df = dfs[i]
                    df['date'] = datestr(vdates[i])
                    for x in range(len(df['times'])):
                        df['times'][x] = float(df['times'][x])
                
                historicaldiscountcurve.curves = dfs
                
            discountcurves.curves.append(historicaldiscountcurve)
        alldiscountcurves.alldiscountcurves.append(discountcurves)
    return alldiscountcurves
                    
                    
                    




    









    

                    








