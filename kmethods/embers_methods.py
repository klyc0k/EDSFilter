# -*- coding: utf-8 -*-
"""
Created on Thu Oct 24 16:29:04 2013

@author: Kevin

EMBERS project specific method set
"""
from datetime import date
import warning_format

class kembers():
    @staticmethod
    def generate_warning(country, location, event_date, event_type='0161', confidence=0, embers_ids=[]):
        """
        format the detection result and the data to the EMBERS warning format for submission.
        """        
        warning0 = [0] * 7        
        warning0[0] = location ## location
        warning0[1] = event_type  ## subtype
        warning0[2] = 'General Population'  ## population
        warning0[3] = [0]*3
        dd = date(int(event_date[0:4]),int(event_date[5:7]),int(event_date[8:10]))
#        dd += datetime.timedelta(days=1) ## add 1 day
        warning0[3][2] = str(dd) + 'T00:00:00' ## event date
        warning0[3][0] = warning0[3][2]
        warning0[3][1] = warning0[3][2]
        warning0[4] = location
        warning0[5] = confidence
        warning0[6] = embers_ids # embers_ids of original tweets
        surrogate = warning_format.formatting_surrogate_dict(warning0)
        msg0 = surrogate, confidence, {}
        w = warning_format.formatting_warning(msg0)
        w = kembers.additional_metrcis(w)
                    
        return w
    @staticmethod  
    def additional_metrcis(w):
        warning = {}
        warning['derivedFrom'] = w['derivedFrom']
        #warning['derivedFrom']['source'] = "Raw Data-Sift Twitter Stream"
        #warning['derivedFrom']['end'] = end_time.replace(" ","T")
        #warning['derivedFrom']['start'] = start_time.replace(" ","T")
        warning['comments'] = "Transfer Learning model"
        warning['model'] = 'Transfer Learning'
        warning['confidence'] =w['confidence']
        warning['confidenceIsProbability'] = True
        warning['eventType'] = w['eventType']
        warning['location'] = w['location']
        warning['coordinates'] = w['coordinates']
        warning['population'] =  w['population']
        #warning['eventDate'] = event_time.replace(" ","T")
        #warning['date'] = end_time.replace(" ","T")
        warning['eventDate'] = w['eventDate']
        warning['date'] = w['date']
        warning['embersId'] =  w['embersId']
        warning['mitreId'] =  w['embersId']
        temp=[]
        temp.append(w['population'])
        temp.append(w['eventType'])
        temp.append(w['eventDate'])
        temp.append((w['location'][0],w['location'][1],w['location'][2]))
        warning['mitreMessage'] = '1145,'+str(temp)+','+str(w['confidence'])
        return warning
