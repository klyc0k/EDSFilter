# -*- coding: utf-8 -*-
"""
Created on Mon Oct 07 10:32:35 2013

@author: Kevin
"""

import countryinfo
from kmethods import kgen


j = kgen.jload("country_db.json")

newdict = dict()

for c in countryinfo.countries:
    subdict = c
    cname = subdict['name'].lower()
    if(j.has_key(cname)):
        subdict['adjective'] = j[cname]
    newdict[cname] = subdict
    
    
for c in j.keys():
    if not newdict.has_key(c):
        subdict =dict()
        subdict['adjective'] = j[c]
        newdict[c] = subdict
        
kgen.jsave(newdict, "./newdict.json")
print len(newdict)


