# -*- coding: utf-8 -*-
"""
Created on Sat Sep 28 16:25:17 2013

@author: Kevin


use for interactive labeling system
"""
from liblinearutil import train, predict, evaluations
#from svmfilter import SVMFilter
import svmfilter

def gen_training_vectors_xy(wordspace_vectors, vecsize, human_labels):
    X = []
    Y = []
    
    i = 0
    for (tid, lbl) in human_labels.items():    
        i+=1
        num_words = 0
        if(not wordspace_vectors.has_key(tid)):
            print "skip"
            continue        
        
        inf = wordspace_vectors[tid]
        newinf = dict([(k+1,v) for k,v in inf.items()])
        num_words = sum(inf.values())
#        if(i<30):
#            print lbl, inf
#        vector = [0] * vecsize
#        for (feat, freq) in inf.items():
#            vector[int(feat)] = freq
#            num_words += freq

        if(num_words <= 5): ## skip the tweets less than 5 valid words
            continue
        
        X.append(newinf)
        Y.append(lbl)
    return Y, X

def gen_training_vectors_xy_new(wordspace_vectors, human_labels):
    """
    New for after 11/13 feature space
    """
    X = []
    Y = []
    
    i = 0
    for (tid, lbl) in human_labels.items():    
        i+=1
        if(not wordspace_vectors.has_key(tid)):
#            print tid
            continue        
        
        inf = wordspace_vectors[tid]

        X.append(inf)
        Y.append(lbl)
    return Y, X

def gen_training_vectors_xy_enhancing(wordspace_vectors, vecsize, human_labels, enhance_level_map):
    X = []
    Y = []
    
    i = 0
    for (tid, lbl) in human_labels.items():    
        i+=1
        num_words = 0
        if(not wordspace_vectors.has_key(tid)):
            print "skip"
            continue        
        
        inf = wordspace_vectors[tid]
        newinf = dict([(k+1,v) for k,v in inf.items()])
        num_words = sum(inf.values())
#        if(i<30):
#            print lbl, inf
#        vector = [0] * vecsize
#        for (feat, freq) in inf.items():
#            vector[int(feat)] = freq
#            num_words += freq

        if(num_words <= 0): ## skip the tweets less than 5 valid words
            continue
        
        if(enhance_level_map.has_key(tid)):
            for j in range(enhance_level_map[tid]):
                X.append(newinf)
                Y.append(lbl)
        else:
            X.append(newinf)
            Y.append(lbl)
            
    print "Lenght of training vectors: %d" % len(Y)
    return Y, X
    
def svm_model_train(Y, X):
    """
    below for reference (parameters to liblinear):
    ------------------------------
    options:
        -s svm_type : set type of SVM (default 0)
        	0 -- C-SVC
        	1 -- nu-SVC
        	2 -- one-class SVM
        	3 -- epsilon-SVR
        	4 -- nu-SVR
        -t kernel_type : set type of kernel function (default 2)
        	0 -- linear: u'*v
        	1 -- polynomial: (gamma*u'*v + coef0)^degree
        	2 -- radial basis function: exp(-gamma*|u-v|^2)
        	3 -- sigmoid: tanh(gamma*u'*v + coef0)
        -d degree : set degree in kernel function (default 3)
        -g gamma : set gamma in kernel function (default 1/num_features)
        -r coef0 : set coef0 in kernel function (default 0)
        -c cost : set the parameter C of C-SVC, epsilon-SVR, and nu-SVR (default 1)
        -n nu : set the parameter nu of nu-SVC, one-class SVM, and nu-SVR (default 0.5)
        -p epsilon : set the epsilon in loss function of epsilon-SVR (default 0.1)
        -m cachesize : set cache memory size in MB (default 100)
        -e epsilon : set tolerance of termination criterion (default 0.001)
        -h shrinking: whether to use the shrinking heuristics, 0 or 1 (default 1)
        -b probability_estimates: whether to train a SVC or SVR model for probability estimates, 0 or 1 (default 0)
        -wi weight: set the parameter C of class i to weight*C, for C-SVC (default 1)
    """
#    traces = []
#    for c in [5,10,15]:
##        acc = train(Y, X,'-v 10 -c {0} -w1 100 -w0 1 -q '.format(c))
#        acc = train(Y, X,'-v 10 -c {0} -w1 100 -w0 1 -q '.format(c))
#        traces.append([c, acc])
##        print 'c={0}'.format(c), acc
#    c = max(traces, key=lambda item: item[1])[0]
#    model=train(Y, X,'-c {0} -w1 100 -w0 1 -q'.format(c))
    model=train(Y, X,'-c 10 -w1 2 -w0 1 -q')
    p_label, p_acc, p_val = predict(Y,X,model)
    ACC, MSE, SCC = evaluations(Y, p_label)
    return model, (ACC, MSE, SCC)

def svm_model_train2(Y, X, weight):
    model=train(Y, X,'-c 10 -w1 {0} -w0 1 -q'.format(weight))
    p_label, p_acc, p_val = predict(Y,X,model)
    ACC, MSE, SCC = evaluations(Y, p_label)
    return model, (ACC, MSE, SCC)

def predict_labels(wordspace_vectors, vecsize, tweets, model, feature_dist):
#    X = tweets_2_X(vocab, tweets)
    svmf = svmfilter.SVMFilter(targetcountry='mexico')
    svmf.load_tweet_vectors_dict(wordspace_vectors)
    
    X, hash2originalID = svmf.extract_vectors(tweets)
    Y = []
    
    if(len(X) == 0):
        return []

    p_label, p_acc, p_val = predict(Y, X, model, '-q')
    
    if(feature_dist):
        p_label = deny_trivial_positive_labels(p_label, X, feature_dist)
    
    Y = [0] * len(tweets)
    for i, pred in enumerate(p_label):
        if pred == 1:
            Y[hash2originalID[i]] = 1
#    X = []
#    for tw in tweets:
#        inf = wordspace_vectors[tw['embersId']]
#        vector = [0] * vecsize
#        for (feat, freq) in inf.items():
#            vector[int(feat)] = freq
#        X.append(vector)
#    
#    Y = []
#    p_label, p_acc, p_val = predict(Y,X,model, '-q')
    return Y
    
def predict_labels_by_tids(wordspace_vectors, vecsize, tweetids, model):
#    X = tweets_2_X(vocab, tweets)
    X = []
    
    for tid in tweetids:
        if(not wordspace_vectors.has_key(tid)):
            tmp = {1:1}
            X.append(tmp)
            print "loss vector"
            continue        
        inf = wordspace_vectors[tid]
#        print inf
#        newinf = dict((k+1,v) for (k,v) in inf.items()) v1113 before
#        X.append(newinf)

        X.append(inf)
    
    Y = []
    p_label, p_acc, p_val = predict(Y,X,model, '-q')
    
    return p_label

def get_predict_vectors_x(wordspace_vectors, tweetids):
#    X = tweets_2_X(vocab, tweets)
    X = []
    
    for tid in tweetids:
        if(not wordspace_vectors.has_key(tid)):
            tmp = {1:1}
            X.append(tmp)
            print "loss vector"
            continue        
        inf = wordspace_vectors[tid]
#        print inf
        newinf = dict((k+1,v) for (k,v) in inf.items())
        
        X.append(newinf)

    return X

def get_predict_vectors_x_new(wordspace_vectors, tweetids):
    """
    for version after feature space 1113
    """
#    X = tweets_2_X(vocab, tweets)
    X = []
    count = 0
    for tid in tweetids:
        if(not wordspace_vectors.has_key(tid)):
            tmp = {1:1}
            X.append(tmp)
#            print "%s loss vector" % tid
            count += 1
            continue        
        inf = wordspace_vectors[tid]
        
        X.append(inf)

    print "%d no vector" % count
    return X

def deny_trivial_positive_labels(Y, X, feature_dists, cutoff=-0.1,strong=-0.2, strongNegative=1):
    """
    feature_dists is 1-based feature distance to the boundary hyperplane
    """
#    print "Deny!"
    
    for i in range(len(Y)):
        if(Y[i] == 1):
            #check X
            inf = X[i]
#            if(len(inf) > 3):###he
#                continue
#            flag = True
            scount = 0
            sn_count = 0
            if((inf.has_key(9255) or inf.has_key(2821) or inf.has_key(19199)) and (inf.has_key(8789) or inf.has_key(9268))):
#            if((inf.has_key(6177) or inf.has_key(4506) or inf.has_key(1648)) and (inf.has_key(5201) or inf.has_key(11485))):
                # if (protest, protesta, protestan) and (march, marcha)
                Y[i] = 1
                continue
            
            if( (inf.has_key(8) and inf[8] > 0.9) and (inf.has_key(9) and inf[9]==1.0)): # if not matching any bigram or trigram
                Y[i] = 0
                continue
            if(inf.has_key(13313)): ## @zodiacohoy
                Y[i] = 0
                continue            
            if(inf.has_key(23791) and not (inf.has_key(19276) or inf.has_key(3403) or inf.has_key(5913))): 
#            if(inf.has_key(4214) and not (inf.has_key(6774) or inf.has_key(9105) or inf.has_key(1792))): 
                # if [FOREIGN] but not embassy nor embajadas or embajada
                Y[i] = 0
                continue
            if(inf[2] == 1):
                continue
            
            for fea in inf.keys():
#                if(fea != 14274 and fea != 14273 and fea != 14275 and fea != 14276 and fea != 14277):
                 if(fea != 1 and fea != 2 and fea != 3 and fea != 4 and fea != 5 and fea != 6 and fea != 7 and fea != 8 and fea != 9):
                    if(feature_dists[str(fea)] < strong):            
                        scount +=1
                    if(feature_dists[str(fea)] > strongNegative):
                        sn_count += 1
                #                if(feature_dists[str(fea)] < cutoff):
#                    flag = False
            
#            if(flag):
#                Y[i] = 0
#            if(scount < 2 or sn_count > 4):
            if(scount < 2):
                Y[i] = 0
            #14274 emoji, #11818 [jaja] #13999 [foreign] #7615 [domestic]
#            if(inf.has_key(14274) and inf[14274] == 1): # hard rejection
#                Y[i] = 0
#            if(inf.has_key(11818) and inf[11818] == 1):
#            if(inf.has_key(3356) and inf[3356] == 1): # denyJAJA
            if(inf.has_key(24442) and inf[24442] == 1): # denyJAJA
                Y[i] = 0
#            elif(inf.has_key(13999) and inf[13999] == 1): # hard rejection
#                Y[i] = 0
    return Y
    
