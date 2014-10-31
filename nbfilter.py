# -*- coding: utf-8 -*-
"""
Created on Wed Dec 11 18:19:42 2013

@author: Kevin

Twitter data filter based on Naive-Bayes classifier
"""

import os
from kmethods import ktwi, kgen # my personal method package
from filterutils import extract_vectors
#from sklearn import naive_bayes

class NBFilter:
    def __init__(self, model_path=None, vocab_path=None, targetcountry=None):
        self._fd = None
        self._tv = None
        if(model_path==None and vocab_path==None):
            classfolder = os.path.dirname(os.path.abspath( __file__ ))
            self.load_nbmodel(classfolder + '/nb_model')
            self.load_vocab(classfolder+ '/svm_vocab.json')
            self._vecsize = len(self._vocab)
#            print "need model and vocab"
        if(model_path != None):
            self.load_svmmodel(model_path)
#            print "need model and vocab"
        
        if(vocab_path != None):
            self.load_vocab(vocab_path)
#            print "need model and vocab"

        self.ktw = ktwi()
        self.ktw.setTargetCountry(targetcountry)
        
    def load_nbmodel(self, filepath):
        if(os.path.exists(filepath)):
            self._model = kgen.pload(filepath)
        else:
            raise IOError(filepath + ': Model file not found.')
            
    def load_vocab(self, filepath):
        if(os.path.exists(filepath)):         
            self._vocab = kgen.jload(filepath)
        else:
            raise IOError(filepath + ': Vocabulary file not found.')
            
    def load_feature_dist(self, filepath):
        if(os.path.exists(filepath)):         
            self._fd = kgen.jload(filepath)
        else:
            raise IOError(filepath + ': feature_dist file not found.')

    def load_tweet_vectors(self, filepath):
        if(os.path.exists(filepath)):         
            self._fd = kgen.jload(filepath)
        else:
            raise IOError(filepath + ': tweet_vectors file not found.')
    
    def load_tweet_vectors_dict(self, tid2vectors):
        self._tv = tid2vectors

    def filter_tweets(self, tweets, text_lookup_field_name='text', deny_no_vector=False):
        noncosider = [3876, 2800]
        tweets = [a for a in tweets if len(a['text'].split()) > 7] # filter tweets less than 7 words
               
        if(len(tweets) ==0):
            return []
        
        filtered_tweets = []
        
        X, hash2originalID = extract_vectors(tweets, self.ktw, self._vocab)
        newX = []
        for x in X:
            tran = dict([(k,v) for k, v in x.items() if(not k in noncosider and v != 0)])
            newX.append(tran)
        
        newX = kgen.dict2dok(newX, self._vecsize, base_adjust = -1)
        
        p_label = self._model.predict(newX)
        for i, pred in enumerate(p_label):
            if pred == 1:
                filtered_tweets.append(tweets[hash2originalID[i]])
                    
        return filtered_tweets
        
    def filter_one_file(self, filepath, text_lookup_field_name='text',deny_no_vector=False):
        """
        filter one data file
        """
        if(not os.path.exists(filepath)):            
            raise IOError('\"%s\"Tweet file not found.' % filepath)
        if(self._model == None or self._vocab == None):
            raise Exception("Load model and vocabulary before filtering.")
        
        # filtering
        tweets = kgen.jload(filepath)
        return self.filter_tweets(tweets, text_lookup_field_name=text_lookup_field_name, deny_no_vector=deny_no_vector)        