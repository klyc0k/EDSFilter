# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 15:25:00 2013

@author: Kevin

for personal convinience. most of codes are copied from others
"""
#from feature_extraction.text import FeatureCountVectorizer
from translate import Translator
import re
from kmethods import kgen
import os, kmethods
from nltk.corpus import stopwords
import unicodedata
from nltk.util import ngrams

class ktwi():
#    NonTargetCountry = ['spain','itlay','egypt','united states','u.s.','japan','china','korea','afghanistan','pakistan','israle','india','eurpoe','uk','u.k.','united kingdom','england','arab','australia','france','germany','canada']
    def __init__(self):    
        self.NonTargetCountries = dict()
        self.TargetCountries = None
        tmpsw = stopwords.words('english') + stopwords.words('spanish')
        self.stopwords = dict(zip(tmpsw, range(len(tmpsw))))
        self.url_pattern = re.compile(r'^.*(https?://[^\s]+).*$', re.I)
        self.jaja_pattern = re.compile('^[j|a]+$', re.I)
        self.emoji_pattern= re.compile("^.*[X|:|;|=]\'?-?[\)|\\|D|P|\||>|\(].*$", re.I)
        self.key_keywords = None
        self.qmark_pattern = re.compile("^.*\?+.*$", re.I)
        
    def setTargetCountry(self, targetcountrynames, language='es'):
        path = os.path.join(kmethods.__path__[0], 'new_country_db.json')
        translator = Translator(from_lang='en',to_lang='es')        
        
        hashtable = kgen.jload(path)
        
        targettable = dict()
        if(type(targetcountrynames)==list):            
            for n in targetcountrynames:
                try:
                    if(type(n)==unicode):
                        n = unicodedata.normalize('NFKD', n).encode('ascii','ignore').lower()
                    transn = translator.translate(n).lower()
                    targettable[n] = hashtable.pop(n)
                    if(hashtable.has_key(transn)):
                        targettable[transn] = hashtable.pop(transn)
                except:
                    print "name %s not found" % n
        elif(type(targetcountrynames)==str or type(targetcountrynames)==unicode):
            try:
                if(type(targetcountrynames)==unicode):
                    targetcountrynames = unicodedata.normalize('NFKD', targetcountrynames).encode('ascii','ignore').lower()
                transn = translator.translate(targetcountrynames).lower()
#                transn = u'm\u00e9xico'
                targettable[targetcountrynames] = hashtable.pop(targetcountrynames)
                if(hashtable.has_key(transn)):
                    targettable[transn] = hashtable.pop(transn)
            except:
                print "name %s not found" % targetcountrynames
        else:
            print "please input list or string"
            return
            
        allterms = [k for t in hashtable.values() for k in t.values()]
        self.NonTargetCountries = dict(zip(allterms, range(len(allterms))))
        alltargets = [k for t in targettable.values() for k in t.values()]
        self.TargetCountries = dict(zip(alltargets, range(len(alltargets))))
    
    def setKey_Keywords(self, keykeywords):
        if(type(keykeywords) == list):
            self.key_keywords = dict(zip(keykeywords, range(0, len(keykeywords))))
        elif(type(keykeywords) == dict):
            self.key_keywords = keykeywords
        else:  
            print "key keywords should be list or dict"
    
    def extract_features(self, text, unmatch_feature=False, vocab=None, verbose=False):
        if(self.TargetCountries == None):
            print "Set target country first."
            return None
            
        transtext = self.trans_stem(text)
#########test
#        transtext = ktwi.remove_stop_words(transtext, language='english')
#        transtext = ktwi.remove_stop_words(traallvocab.append('[POS_$KEYWORD$]')nstext, language='spanish')
        transtext = self.remove_stop_words_quick(transtext)
#########        
        terms = re.split(',|\.|\"| |;|:',transtext)
        
        if(unmatch_feature == True):
            (features, vec1, vec2, vec3) = ktwi.extract_terms_features(terms, separateGrams= True)
            
#            print "vec1: %s" % str(vec1)
#            print "vec2: %s" % str(vec2)
#            print "vec3: %s" % str(vec3)
            
            matched1 = len([ff for ff in vec1.keys() if vocab.has_key(ff)])
            matched2 = len([ff for ff in vec2.keys() if vocab.has_key(ff)])
#            print [ff for ff in vec2.keys() if vocab.has_key(ff)]
#            print matched2
            
            matched3 = len([ff for ff in vec3.keys() if vocab.has_key(ff)])
            
            if(len(features) != 0):
                features['[MISSEDFT_ALL]'] = (len(features) - (matched1 + matched2 + matched3) + 0.0 ) / (len(features) + 0.0)
            if(len(vec1) != 0):
                features['[MISSEDFT_G1]'] = ((len(vec1) - matched1) + 0.0) /  (len(vec1) + 0.0)
            if(len(vec2) != 0):
                features['[MISSEDFT_G2]'] = ((len(vec2) - matched2) + 0.0) /  (len(vec2) + 0.0)
            if(len(vec3) != 0):
                features['[MISSEDFT_G3]'] = ((len(vec3) - matched3) + 0.0) /  (len(vec3) + 0.0)
            
            if(verbose == True):
                print "input text: %s" % unicodedata.normalize('NFKD', text).encode('ascii','ignore')
                print "extracted features: %s" % str(features)
            
            return features
                    
        else:
            features = ktwi.extract_terms_features(terms)
            if(verbose == True):
                print "input text: %s" % unicodedata.normalize('NFKD', text).encode('ascii','ignore')
                print "extracted features: %s" % str(features)
            return features
    
    def extract_artificial_features(self, text):
        """
        extract the artificial features such as [LINK], [EMOJI], [NWORDS], [POS_$KEYWORD$],
        [MDUPL], [SENTIMENT], [QMARK].
        
        return a dict contain the value of the above features
        """
        art_feat = dict()
        if(self.url_pattern.match(text) != None):
            art_feat['[LINK]'] = 1
        else:
            art_feat['[LINK]'] = 0
        
        if(self.emoji_pattern.match(text) != None):
            art_feat['[EMOJI]'] = 1
        else:
            art_feat['[EMOJI]'] = 0
        
        art_feat['[NWORDS]'] = len(text.split(' ')) /10.0 ##!!
        
        stext = re.split('\.|,| ',text)
#        for i, t in enumerate(stext):
#            if self.key_keywords != None and self.key_keywords.has_key(t):
#                art_feat['[POS_$%s$]' % t] = i + 1
        
        maxdup = max([stext.count(x) for x in stext])
        if(maxdup > 1):
            art_feat['[MDUPL]'] = maxdup / 10.0
        
        if(self.qmark_pattern.match(text) != None):
            art_feat['[QMARK]'] = 1
        else:
            art_feat['[QMARK]'] = 0

        return art_feat
        # no sentiment tool for esp now
    
    def trans_stem(self, x):
        x = re.sub('\n|\)|\(', '', x)
        x = re.sub('@ ', ' ', x)
        if(type(x) == unicode):
            x=kgen.normalize_unicode(x)
#        x = ktwi.remove_urls(x)
        # first deal with these patterns
#        emoji_pattern= re.compile("[X|:|;|=]\'?-?[\)|\\|D|P|\||>|\(]", re.I)
#        emoji_pattern.sub(" [EMOJI] ", x)
        jaja_pattern = re.compile('^a?[h|j]+[h|j|a]+$', re.I)
#        jaja_pattern.sub(" [JAJA] ", x)
        url_pattern = re.compile('http[s]?://[^\s<>"]+|www\.[^\s<>"]+')
        x = url_pattern.sub("", x)
        
        
        tokens = re.split(' |,|\.|\"|;', x)
        
#        if len(tokens) <= 1:
#            return x
            
        ok_tokens = []
        # filter country
        possess_pattern = re.compile('\w+[:|\'s|s\']')
        pavoid = re.compile(':|\'s|s\'')
        hashtag_pattern = re.compile('#\w+')
        havoid = re.compile('#')        
        
        for term in tokens:
            term = term.lower()
            poflag = False
            if(possess_pattern.match(term) != None):
                checkingterm = pavoid.sub('',term)
                poflag = True
            elif(hashtag_pattern.match(term) != None):
                checkingterm = havoid.sub('',term)
            else:
                checkingterm = term
                
            if self.TargetCountries.has_key(checkingterm):
                ok_tokens.append("[DOMESTIC]")
            elif self.NonTargetCountries.has_key(checkingterm):
                ok_tokens.append("[FOREIGN]")                
            elif jaja_pattern.match(re.sub("[\d\W]+",'',term)):
                ok_tokens.append("[JAJA]")
                
#            if self.TargetCountries.has_key(checkingterm):
#                ok_tokens.append(" [THISCOUNTRY] ")
#            elif self.NonTargetCountries.has_key(checkingterm):
#                ok_tokens.append(" [FOREIGNCOUNTRY] ")
            else:
                if(poflag):
                    ok_tokens.append(checkingterm)
                else:
                    ok_tokens.append(term)
        
        return u' '.join([token for token in ok_tokens if len(token) > 0])
        
    @staticmethod    
    def extract_terms_features(terms, separateGrams=False):
        vector = dict()
        
        while('' in terms):
            terms.remove('')
#        for term in terms:
#            if vector.has_key(term):
#                vector[term] += 1
#            else:
#                vector[term] = 1
#        for i in range(len(terms) - 2):
#            cb2 = ' '.join(terms[i:i+1])
#            cb3 = ' '.join(terms[i:i+2])
#            if vector.has_key(cb2):
#                vector[cb2] += 1
#            else:
#                vector[cb2] = 1
#            if vector.has_key(cb3):
#                vector[cb3] += 1
#            else:
#                vector[cb3] = 1
#        cb2 = ' '.join(terms[len(terms)-2:len(terms)])
#        if vector.has_key(cb2):
#            vector[cb2] += 1
#        else:
#            vector[cb2] = 1
#        print terms
        g2 = ngrams(terms, 2)
        g3 = ngrams(terms, 3)
        
        
        g2j = [' '.join(gterms) for gterms in g2]
        g3j = [' '.join(gterms) for gterms in g3]
        
        
        vec1 = {}
        vec2 = {}
        vec3 = {}
        
        for t in terms:
            if(not vector.has_key(t)):
                vec1[t] = 1
            else:
                vec1[t] += 1
        for t in g2j:
            if(not vector.has_key(t)):
                vec2[t] = 1
            else:
                vec2[t] += 1
        for t in g3j:
            if(not vector.has_key(t)):
                vec3[t] = 1
            else:
                vec3[t] += 1
        
        vector = dict(vec1.items() + vec2.items() + vec3.items())
        if(separateGrams == True):
            return (vector, vec1, vec2, vec3)
        else:
            return vector

    @staticmethod
    def features_to_vector(vocab, features):
        vector = [0] * len(vocab)
        for feat, freq in features.items():
            if vocab.has_key(feat.lower()):
                vector[vocab[feat.lower()]] = freq
        return vector
    @staticmethod
    def features_to_dict(vocab, features, art_features):
        """
        returns hash dict
        definition revised at 11.18.2013
        """
        dc = dict()
        for feat, freq in features.items():
            if vocab.has_key(feat):
                dc[int(vocab[feat])] = freq
        if(art_features):
            for feat, val in art_features.items():
                if vocab.has_key(feat):
                    dc[int(vocab[feat])] = val
        return dc
    @staticmethod
    def features_to_dict_1_based(vocab, features):
        """
        returns 1-based hash dict
        """
        dc = dict()
        for feat, freq in features.items():
            if vocab.has_key(feat.lower()):
                dc[int(vocab[feat.lower()])+1] = freq
        return dc    
    @staticmethod
    def features_to_dict_0_based(vocab, features):
        """
        returns 0-based hash dict
        """
        dc = dict()
        for feat, freq in features.items():
            if vocab.has_key(feat.lower()):
                dc[int(vocab[feat.lower()])] = freq
        return dc
                
    @staticmethod
    def is_entity(term):

        uterm =  term.upper()
        match = re.search('[A-Z]{1,3}[-|/]{0,1}[0-9]{1,4}[-|/]{0,1}[ABNWESR]{0,3}', uterm)
        if match and match.group() == uterm:
            return True
            
        match = re.search('[0-9]{1,4}[-|/]{0,1}[ABNWESR]{0,3}[-|/]{0,1}[A-Z]{1,3}', uterm)
        if match and match.group() == uterm:
            return True

        match = re.search('[ABNWESR]{2,3}', uterm)
        if match and match.group() == uterm:
            return True

        if term[0] in ['@', '#']:
            return True
            
        if term.isdigit():
            return True
            
        return False
    
    @staticmethod
    def freqVec2dict(freqvec):
        fd = dict()
        for i in range(len(freqvec)):
            if(freqvec[i] != 0):
                fd[int(i)] = freqvec[i]
        return fd
    
    @staticmethod
    def remove_urls(text):
        for url in re.findall(r'(https?://[^\s]+)', text):
            text = text.replace(url, '')
        return text
        
    @staticmethod
    def get_countries():
        import pycountry
        allcountries = []
        for country in list(pycountry.countries):
            allcountries.append(country.name.lower())
        return allcountries   

    def remove_stop_words_quick(self, text):
        """
        remove all stop words in english and spanish
        require initialization to this class
        """
        text_items = ktwi.remove_symbols(text).split()
        tmp = []
        for t in text_items:        
            if(not self.stopwords.has_key(t)):
                tmp.append(t)
        
        return ' '.join(te for te in tmp)
    
    @staticmethod
    def remove_stop_words(text, language='english'):
        """
        remove all stop words in a specified language, default= english
        """
        text_items = text.split()
        tmp = []
        for t in text_items:
            newt = ktwi.remove_symbols(t)
            if(not newt in stopwords.words(language)):
                tmp.append(t)
        
        return ' '.join(te for te in tmp)
        
    @staticmethod
    def remove_symbols(text):
        """
        remove all symbols except \' and whitespaces
        """
        return re.sub(r'[^\w\d\'[] ]', '', text)
        
            