# -*- coding: utf-8 -*-
"""
Created on Wed Dec 11 17:47:55 2013

@author: Kevin
"""

import pyparsing as pp
import json

def extract_vectors(tweets, ktwi_object, vocab, text_lookup_field_name='text'):
    """
    extract tweets to training vectors, disgard tweets with no features
    return the valid vectors with a hash to their original ID
    """
    X = []
    i = 0
    j = 0
    hash2originalID = dict()
    for tweet in tweets:
        features = extract_single_vector(tweet, ktwi_object, vocab, text_lookup_field_name)
        if(not len(features)<4):
            hash2originalID[j] = i
            X.append(features)
            j+=1
        i+=1
        
    return X, hash2originalID

def extract_single_vector(tweet, ktwi_object, vocab, text_lookup_field_name='text'):
    text = tweet[text_lookup_field_name]
    features = ktwi_object.features_to_dict(vocab, ktwi_object.extract_features(text, True, vocab), ktwi_object.extract_artificial_features(text))
    
    return features
    

def load_rules(filepath):
    operator = pp.Regex(">=|<=|!=|>|<|==").setName("operator")
    number = pp.Regex(r"[+-]?\d+(:?\.\d*)?(:?[eE][+-]?\d+)?")
    identifier = pp.Word(pp.alphas + "[]", pp.alphanums + "_[]")
    comparison_term = identifier | number
    a_comparison = comparison_term + operator + comparison_term
    stmt = a_comparison | identifier
    condition = pp.Group(stmt)
    
    expr = pp.operatorPrecedence(condition,[
                                ("NOT", 1, pp.opAssoc.RIGHT, ),
                                ("AND", 2, pp.opAssoc.LEFT, ),
                                ("OR", 2, pp.opAssoc.LEFT, ),
                                ])
    
    rules = []
    with open(filepath,'r') as f:
        lines = f.readlines()
        for line in lines:
            rule_and_acceptance = line.split("=>")
            ptree = expr.parseString(rule_and_acceptance[0].strip())
            acceptance = True if rule_and_acceptance[1].strip() == 'True' else False
            rules.append((json.loads(ptree[0].dump().replace("\'","\"")), acceptance)) # make flat list
            
    return rules