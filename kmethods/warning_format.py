# -*- coding: utf-8 -*-
__author__ = 'Liang Zhao'
__email__ = 'liangz8@vt.edu'
__version__ = '1.0.0'

import hashlib
import unicodedata

def get_hash_key(x):
    return hashlib.sha1(str(x)).hexdigest()

def normalize_str(s):
    if isinstance(s, str):
        s = s.decode("utf8")
    s = unicodedata.normalize("NFKD", s)
    return s.encode('ASCII', 'ignore').lower()

CO_CAPITAL_OSI_WAY = {
    'Ciudad de México': ['Mexico', 'Ciudad de México', 'Ciudad de México'],
    'Brasília'	      : ['Brazil', 'Brasília', 'Brasília'],
    'Buenos Aires'    : ['Argentina', '-', 'Buenos Aires'],
    'Caracas'         : ['Venezuela', 'Caracas', 'Caracas'],
    'Bogotá'          : ['Colombia', 'Bogotá', 'Bogotá'],
    'Quito'           : ['Ecuador', 'Pichincha', 'Quito'],
    'San Salvador'    : ['El Salvador', 'San Salvador', 'San Salvador'],
    'Asunción'        : ['Paraguay', 'Asunción', 'Asunción'],
    'Montevideo'      : ['Uruguay', 'Montevideo', 'Montevideo']
}

CO_CAPITAL_LOOKUP = dict( (normalize_str(k), v) for k, v in CO_CAPITAL_OSI_WAY.iteritems())

def osi_capital_city_province_corrector(loc):
    """Makes the state info correction as per OSI for
       capital city of the country

    :param loc: location tuple (Country, State, City)
    :returns: ( Country, State, City )
    """
    ci = normalize_str(loc[2])
    if ci in CO_CAPITAL_LOOKUP and \
       normalize_str(loc[0]) == normalize_str(CO_CAPITAL_LOOKUP[ci][0]):
        return CO_CAPITAL_LOOKUP[ci]
    else:
        return loc

def formatting_warning(msg0):
    surrogate, possibility, eIdKeyword = msg0
    warning = {}
    warning['derivedFrom'] = {}
    warning['derivedFrom']['source'] = "Raw Data-Sift Twitter Stream"
    warning['derivedFrom']['end'] = surrogate['derivedFrom']['end']
    warning['derivedFrom']['start'] = surrogate['derivedFrom']['start']
    warning['comments'] = "Dynamic Query Expansion model(classifier=classification.randomforest-CU v0.0.1)"
    warning['derivedFrom']['derivedIds'] = (surrogate['embersId'],eIdKeyword) # from tweets
    warning['model'] = 'Dynamic Query Expansion model(classifier=classification.randomforest-CU v0.0.1)'
    warning['confidence'] = possibility
    warning['confidenceIsProbability'] = True
    warning['eventType'] = surrogate['eventType']
    warning['location'] = surrogate['location']
    warning['coordinates'] = surrogate['coordinates']
    warning['population'] = surrogate['population']
    warning['eventDate'] = surrogate['eventDate']
    warning['date'] = surrogate['date']
    warning['embersId'] = get_hash_key(warning)
    return warning
def formatting_surrogate_dict(warning0): #surrogate
    warning = {}
    warning['derivedFrom'] = {}
    warning['derivedFrom']['source'] = "Local Modularity Spatial Scan"  
    warning['derivedFrom']['end'] = warning0[3][1]  # last tweet timestamp 
    warning['derivedFrom']['start'] = warning0[3][0]  # first tweet tinestamp
    warning['comments'] = "Local Modularity Spatial Scan(classifier=classification.randomforest-CU v0.0.1)"  
    warning['derivedFrom']['derivedIds'] = warning0[6]   # raw data: embersID, processed data: parent ID
    warning['model'] = 'Local Modularity Spatial Scan(classifier=classification.randomforest-CU v0.0.1)'
    warning['confidence'] = warning0[5]
    warning['confidenceIsProbability'] = True
    warning['eventType'] = warning0[1]
    warning['location'] = osi_capital_city_province_corrector(warning0[0])
    warning['coordinates'] = warning0[4]
    warning['population'] = warning0[2]
    warning['eventDate'] = warning0[3][2]
    warning['date'] = warning0[3][1]
    warning['embersId'] = get_hash_key(warning)
    return warning

def formatting_surrogate(warnings0,dates):
    surrogates = []
    for dat in warnings0:
        location = dat[0][0][0][0]
        coordinates = tuple(dat[0][0][0][1])
        eventType = dat[0][0][1][0]
        population = dat[0][0][1][1]
        confidence = dat[0][1]
        embersId = dat[1]
        surrogates.append(formatting_surrogate_dict((location,eventType,population,
                                                dates,coordinates,confidence,embersId)))
    return surrogates
    
    
def formatting_keywords(country,date,keyspace,embersIds): #eIdKeyword
    temp,keyelements = keyspace
    del temp
    msg = {}
    msg['country'] = country
    msg['keywords'] = keyelements.keys()
    msg['date'] = date[:10]
    msg['derivedFrom'] = embersIds
    msg['embersId'] = get_hash_key(msg)
    return msg
    
def formalizing(surrogates0,threshold,dates,eIdKeyword):
    warnings = []
    for dat in surrogates0:
        confidence = dat['confidence']
        if(confidence>threshold):
            possibility = float('%.3f'%Possibility_computing(confidence,threshold))
            if(possibility >= 0.2):
                warnings.append(formatting_warning((dat,possibility,eIdKeyword)))
    return warnings

def Possibility_computing(count,threshold):
    if(threshold > 0):
        return (count-threshold)*0.8/float(1.0 - threshold)
    else:
        return count*0.8

def main():
    pass

if __name__ == '__main__':
    main()