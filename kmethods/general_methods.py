# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 15:02:47 2013

@author: Kevin

general functions for personal convienience
"""

import json 
import cPickle as pickle
import os
import string
import random
from datetime import timedelta
from datetime import datetime
import unicodedata

class kgen(object):
    @staticmethod
    def jsave(data, filepath):
        """ 
        save json file
        """
        f = open(filepath, "w")
        f.write(json.dumps(data))
        f.close()
        
    @staticmethod
    def jsave_pretty(data, filepath):
        """ 
        save json file
        """
        import simplejson
        f = open(filepath, "w")
        f.write(simplejson.dumps(data, sort_keys = False, indent = 4))
        f.close()     
    @staticmethod
    def jsave_multilines(data, filepath):
        """ 
        save json file
        """
        f = open(filepath, "w")
        for d in data:
            f.write(json.dumps(d) + '\n')
        f.close()
        
    @staticmethod    
    def jload(filepath):
        """
        load json file
        """
        if(not os.path.exists(filepath)):
            print "open %s failed" % filepath
            return None
        json_data = open(filepath, 'r')
        data = json.load(json_data, encoding='utf-8')
        return data
    @staticmethod
    def jload_multilines(filepath, ignore=True):
        """
        load json file (each line is a json object)
        """
        if(not os.path.exists(filepath)):
            print "open %s failed" % filepath
            return None
                    
        f = open(filepath, 'r')
        lines = f.readlines()
        
        if(ignore):
            lines = [line for line in lines if len(line) > 2]
            data = []
            errflag = False
            for line in lines:                
                try:
                    tmp = json.loads(line)
                    data.append(tmp)
                except:
                    errflag = True
                    continue
            if(errflag):
                print "Errors were presented and ignored."
                
        else:
            data = [json.loads(line) for line in lines]        
        return data
        
    @staticmethod    
    def psave(data, filepath):
        """
        save pickle file
        """
        with open(filepath, "wb") as output:
            pickle.dump(data, output, pickle.HIGHEST_PROTOCOL)
    @staticmethod
    def pload(filepath):
        """
        load pickle file
        """
        if(not os.path.exists(filepath)):
            print "open %s failed" % filepath
            return None
        f = open(filepath, "rb")
        obj = pickle.load(f) # protocol version is detected
        return obj
    @staticmethod
    def load_tsv(filepath, header= False, outtype='list'):
        """
        load comma separate file
        header = True if the first line is the header
        outtype = 'list' or 'dict' (only if header is available)        
        """
        f = open(filepath, 'r')
        lines = f.readlines()
        
        if(header):
            if(outtype == 'list'):
                data = [d.split('\t') for d in lines]
            elif(outtype == 'dict'):
                header_columns = lines[0].split('\t')
                data = [dict(zip(header_columns, d.split('\t'))) for d in lines[1:]]
        else:
            data = [d.split('\t') for d in lines]
        return data
    @staticmethod
    def load_delimiter_file(filepath, header= False, delimiter=',', outtype='list'):
        """
        load comma separate file
        header = True if the first line is the header
        outtype = 'list' or 'dict' (only if header is available)        
        delimiter = delimiter, default ',' (csv)
        """
        f = open(filepath, 'r')
        lines = f.readlines()
        
        if(header):
            if(outtype == 'list'):
                data = [d.split(delimiter) for d in lines]
            elif(outtype == 'dict'):
                header_columns = lines[0].split(delimiter)
                data = [dict(zip(header_columns, d.split(delimiter))) for d in lines[1:]]
        else:
            data = [d.split(delimiter) for d in lines]
        return data        
    @staticmethod
    def get_all_fullpaths(folder, startfilter=None, endfilter=None):
        """
        get the full paths under a folder
        """
        files = os.listdir(folder)
        files.sort()
        if(endfilter == None and startfilter==None):
            fullfiles = [os.path.join(folder,f) for f in files]
        elif(startfilter==None and endfilter != None):
            fullfiles = [os.path.join(folder,f) for f in files if f.endswith(endfilter)]
        elif(startfilter!=None and endfilter == None):
            fullfiles = [os.path.join(folder,f) for f in files if f.startswith(startfilter)]
        else:
            fullfiles = [os.path.join(folder,f)for f in files if (f.endswith(endfilter) and f.startswith(startfilter))]
            
        return fullfiles
    @staticmethod
    def get_in_out_fullpaths(infolder, outfolder, startfilter=None, endfilter=None):
        """
        for 1-1 mapping in-n-out files, return a set of tuples of (infile, outfile) in full paths
        """
        files = os.listdir(infolder)
        files.sort()
        if(endfilter == None and startfilter==None):
            fullfiles = [(os.path.join(infolder,f),  os.path.join(outfolder,f)) for f in files]
        elif(startfilter==None and endfilter != None):
            fullfiles = [(os.path.join(infolder,f),  os.path.join(outfolder,f)) for f in files if f.endswith(endfilter)]
        elif(startfilter!=None and endfilter == None):
            fullfiles = [(os.path.join(infolder,f),  os.path.join(outfolder,f)) for f in files if f.startswith(startfilter)]
        else:
            fullfiles = [(os.path.join(infolder,f),  os.path.join(outfolder,f)) for f in files if (f.endswith(endfilter) and f.startswith(startfilter))]
            
        return fullfiles
    @staticmethod
    def get_all_fullpaths_with_fliename(folder, startfilter=None, endfilter=None, recursive=False):
        """
        get the full paths under a folder
        returns tuple list (full_path, filename)
        """
        files = os.listdir(folder)
        files.sort()
        if(endfilter == None and startfilter==None):
            if(recursive==False):
                fullfiles = [(os.path.join(folder, f), f) for f in files]
            else:
                fullfiles = [(os.path.join(dp, f), f) for dp, dn, filenames in os.walk(folder) for f in filenames]
        elif(startfilter==None and endfilter != None):
            if(recursive==False):
                fullfiles = [(os.path.join(folder, f), f) for f in files if f.endswith(endfilter)]
            else:
                fullfiles = [(os.path.join(dp, f), f) for dp, dn, filenames in os.walk(folder) for f in filenames if f.endswith(endfilter)]
        elif(startfilter!=None and endfilter == None):
            if(recursive==False):
                fullfiles = [(os.path.join(folder, f), f) for f in files if f.startswith(startfilter)]
            else:
                fullfiles = [(os.path.join(dp, f), f) for dp, dn, filenames in os.walk(folder) for f in filenames if f.startswith(startfilter)]
        else:
            if(recursive==False):
                fullfiles = [(os.path.join(folder, f), f) for f in files if (f.endswith(endfilter) and f.startswith(startfilter))]
            else:
                fullfiles = [(os.path.join(dp, f), f) for dp, dn, filenames in os.walk(folder) for f in filenames if (f.endswith(endfilter) and f.startswith(startfilter))]
        return fullfiles
        
    @staticmethod
    def load_all_json_list_into_one(infolder, startfilter=None):
        files = kgen.get_all_fullpaths(infolder, startfilter=startfilter, endfilter='.json')
        allj = []
        for f in files:            
            j = kgen.jload(f)
            if(j != None):
                allj += j
        return allj
    @staticmethod
    def mkdir_if_not_exist(folder_path):
        if(not os.path.exists(folder_path)):
            os.mkdir(folder_path)
            
    @staticmethod
    def sort_dict(data, sortby='key',order='desc'):
        """
        return sorted tuple, sortby= 'key' or 'value';order = 'desc' or 'asc'
        """
        
        if(order == 'desc'):
            if(sortby == 'key'):
                a = sorted(data.items(), key=lambda x:x[0])
                a.reverse()
                return a
            else:
                a = sorted(data.items(), key=lambda x:x[1])
                a.reverse()
                return a
        else:
            if(sortby == 'key'):
                return sorted(data.items(), key=lambda x:x[0])
            else:
                return sorted(data.items(), key=lambda x:x[1])
    @staticmethod
    def chunks(l, n):
        """ 
        Yield successive n-sized chunks from l.
        """
        for i in xrange(0, len(l), n):
            yield l[i:i+n]
            
    @staticmethod
    def string_generator(size=10, chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):
        return ''.join(random.choice(chars) for x in range(size))
        
    @staticmethod
    def daterange(start_date, end_date, output_string = None):
        """
        Returns a list of dates within the given range [start_date, end_date]
        Set output_string to get a list of string, e.g. output_string = "%Y-%m-%d"
        """
        d = start_date
        delta = timedelta(days=1)
        datelist = []
        while d <= end_date:
            datelist.append(d)
            d += delta
            
        if(output_string != None):
            datelist = [dd.strftime(output_string) for dd in datelist]
            
        return datelist
    @staticmethod
    def dict2dok(darray, vectorsize, base_adjust=0):
        """
        Convert dict-based sparse vector array to scipy.dok_matrix
        """
        from scipy import sparse
        dokm = sparse.dok_matrix((len(darray),vectorsize))
        for i, d in enumerate(darray):
            for k,v in d.items():                
                dokm[i,k + base_adjust] = v
        return dokm
        
    @staticmethod
    def normalize_unicode(text):
        if(type(text) == str):
            return text
        else:
            return unicodedata.normalize('NFKD', text).encode('ascii','ignore')
    
    @staticmethod
    def unique(seq):
        """
        Removes duplicated entries whilst preserving the order
        """
        seen = set()
        seen_add = seen.add
        return [ x for x in seq if x not in seen and not seen_add(x)]