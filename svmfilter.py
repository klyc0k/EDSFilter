# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 11:02:24 2013

@author: Kevin
"""

import os
from liblinearutil import load_model, predict
from kmethods import ktwi, kgen # my personal method package
from filterutils import extract_vectors, extract_single_vector, load_rules

class SVMFilter:
    def __init__(self, model_path=None, vocab_path=None, targetcountry=None):
        self._fd = None
        self._featrule = None
        self.oper = ['>=','<=','>','<','==']
        
        classfolder = os.path.dirname(os.path.abspath( __file__ ))        
        self.load_hard_reject(classfolder + '/hard_reject.txt')
        
        if(model_path != None):
            self.load_svmmodel(model_path)
        else:
            self.load_svmmodel(classfolder + '/svm_model')
        
        if(vocab_path != None):
            self.load_vocab(vocab_path)
        else:
            self.load_vocab(classfolder+ '/svm_vocab.json')
            
        self.ktw = ktwi()
        self.ktw.setTargetCountry(targetcountry)
        
    def load_svmmodel(self, filepath):
        """
        load svm model
        """
        if(os.path.exists(filepath)):
            self._model = load_model(filepath)
        else:
            raise IOError(filepath + ': Model file not found.')
            
    def load_vocab(self, filepath):
        """
        load vocab
        """
        if(os.path.exists(filepath)):         
            self._vocab = kgen.jload(filepath)            
        else:
            raise IOError(filepath + ': Vocabulary file not found.')
            
    def load_feature_dist_rule(self, fdist_path=None, frule_path=None):
        """
        load feature based hard rule settings
        """        
        if(fdist_path==None):
            classfolder = os.path.dirname(os.path.abspath( __file__ ))
            self._fd = kgen.jload(classfolder + '/feature_dist.json')            
        else:
            if(os.path.exists(fdist_path)):         
                self._fd = kgen.jload(fdist_path)
            else:
                raise IOError(fdist_path + ': feature_dist file not found.')
                
        if(frule_path==None):
            classfolder = os.path.dirname(os.path.abspath( __file__ ))
            self._featrule = load_rules(classfolder + '/feature_rule.txt')            
        else:
            if(os.path.exists(frule_path)):         
                self._featrule = load_rules(frule_path)
            else:
                raise IOError(frule_path + ': feature rule file not found.')        
        
    def load_hard_reject(self, filepath):
        """
        load the hard reject list
        """
        if(os.path.exists(filepath)):         
            f = open(filepath, 'r')
            lines = f.readlines()
            f.close()
            self._hardreject = [term.lower().strip() for term in lines]
        else:
            raise IOError(filepath + ': hard reject file not found.')
    
    def classify_single_tweet(self, tweet, text_lookup_field_name='text'):
        """
        classify a single tweet is cu-related or not
        """
        X = [extract_single_vector(tweet, self.ktw, self._vocab, text_lookup_field_name)]
        Y = []
        p_label, p_acc, p_val = predict(Y, X, self._model, '-q')
        
        if(self._fd and self._featrule):
            p_label = self.hard_feature_rules(p_label, X)
        
        if(self.hard_reject(tweet[text_lookup_field_name])):
            p_label = [0]
            
        return p_label[0] == 1

    def filter_tweets(self, tweets, text_lookup_field_name='text'):
        """
        filter loaded tweets
        """
        tweets = [a for a in tweets if len(a[text_lookup_field_name].split()) > 7] # filter tweets less than 7 words
        
        if(len(tweets) ==0):
            return []
        
        filtered_tweets = []
        if(len(tweets) > 1000000):  ## split into chunks if the size is too big
            tweet_chunks = list(kgen.chunks(tweets, 1000000))
            
            for chnk in range(len(tweet_chunks)):
                print "processing chunk %d" % chnk
                X, hash2originalID = extract_vectors(tweet_chunks[chnk], self.ktw, self._vocab, text_lookup_field_name)
                Y = []
                
                if(len(X) <= 2):
                    continue
                
                p_label, p_acc, p_val = predict(Y, X, self._model, '-q') ###he
                         
                if(self._fd):
                    p_label = self.hard_feature_rules(p_label, X)
                
                for i, pred in enumerate(p_label):
                    if pred == 1:
                        filtered_tweets.append(tweet_chunks[chnk][hash2originalID[i]])        
        else:
            X, hash2originalID = extract_vectors(tweets, self.ktw, self._vocab, text_lookup_field_name)
            Y = []
            
            if(len(X) == 0):
                return []
            
            p_label, p_acc, p_val = predict(Y, X, self._model, '-q') ###he

            if(self._fd):
                p_label = self.hard_feature_rules(p_label, X)                                        
            
            for i, pred in enumerate(p_label):
                if pred == 1:
                    if(not self.hard_reject(tweets[hash2originalID[i]]['text'])):
                        filtered_tweets.append(tweets[hash2originalID[i]])
                    
        return filtered_tweets

    def hard_reject(self, text):
        """
        return true for rejection, false for acception
        hard reject the tweets contains keywords in the list (those may not be in feature space)
        """
        for t in self._hardreject:
            if text.lower().find(t) >= 0:
                return True
        return False
    
    def hard_feature_rules(self, Y, X, cutoff=-0.1,strong=-0.2, strongNegative=1):
        """
        feature_dists is 1-based feature distance to the boundary hyperplane.
        apply feature based rules to accept or reject tweets
        """
        for i in range(len(Y)):
#            if(Y[i] == 1):                
#                inf = X[i]
#                scount = 0
#                sn_count = 0
#                for fea in inf.keys():
#                     if(fea not in range(9)):
#                        if(self._fd[str(fea)] < strong):            
#                            scount +=1
#                        if(self._fd[str(fea)] > strongNegative):
#                            sn_count += 1
#                if(scount < 2):
#                    Y[i] = 0

            for rl, accept in self._featrule: # check all feature based rules
                rule_matching = self.applyRule(rl, X[i])
                if(rule_matching == True):
                    if(accept == True):
                        Y[i] = 1
                        break
                    else:
                        Y[i] = 0
                        break
        return Y
        
    
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
        return self.filter_tweets(tweets, text_lookup_field_name=text_lookup_field_name)


    def applyRule(self, ruleArr, X):
        """
        Check if the rule is matched
        """
        lenarr = len(ruleArr)
        if(lenarr == 1): # check word match
            featidx = self._vocab[ruleArr[0]] # convert rule word to index so X vector can match it
            return (X.has_key(featidx) and X[featidx] > 0)
        elif(lenarr== 3 and ruleArr[1] in self.oper):
            featidx = self._vocab[ruleArr[0]] # convert rule word to index so X vector can match it
            opleft = float(X[featidx])
            if(ruleArr[1] == ">"):
                return opleft > float(ruleArr[2])
            elif(ruleArr[1] == "<"):
                return opleft < float(ruleArr[2])
            elif(ruleArr[1] == "=="):
                return opleft == float(ruleArr[2])
            elif(ruleArr[1] == ">="):
                return opleft >= float(ruleArr[2])
            elif(ruleArr[1] == "<="):
                return opleft <= float(ruleArr[2])
        else:
            BoolVal = None
            OpStack = None
            for item in ruleArr:
                if(type(item) == list):
                    ThisBoolVal = self.applyRule(item, X)
                elif(item == 'AND' or item == 'OR' or item == 'NOT'):
                    ThisBoolVal = None
                    OpStack = item
                if(BoolVal == None):
                    BoolVal = ThisBoolVal
                elif(OpStack != None and ThisBoolVal != None):
                    if(OpStack == 'AND'):
                        BoolVal = all([BoolVal, ThisBoolVal])                    
                    elif(OpStack == 'OR'):
                        BoolVal = any([BoolVal, ThisBoolVal])
                    elif(OpStack == 'NOT'):
                        BoolVal = not ThisBoolVal
                    OpStack = None
            return BoolVal