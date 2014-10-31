# -*- coding: utf-8 -*-
"""
Created on Wed Dec 11 18:06:34 2013

@author: Kevin
"""

from svmfilter import SVMFilter
from nbfilter import NBFilter
from kmethods import kgen

svmf = SVMFilter(targetcountry='mexico')

# filter simply by a given file path
filtered_tw = svmf.filter_one_file(r'2012-07-04.json')

# or
# filter by loaded tweets

tweets = kgen.jload(r'2012-07-04.json')
print "# before filter: %d" % len(tweets)

filtered_tw = svmf.filter_tweets(tweets)

print "# after filtered: %d" % len(filtered_tw)

# with some explicit rule rejection
svmf.load_feature_dist_rule()

filtered_tw = svmf.filter_tweets(tweets)
print "# with rule rejection: %d" % len(filtered_tw)

print '-' * 20 + "Filtered Tweets" + '-' * 20
for x in filtered_tw:
    print kgen.normalize_unicode(x['text'])
    print '-' * 30

# if you would like to classify a single tweet
print "-" * 20 + "Test a single tweet" + "-" *20
print tweets[0]
print "-" * 50
print "If this is a positive tweet say True ------", svmf.classify_single_tweet(tweets[0])

print "-" * 50

# if you would like to see a result that using a Naive-Bayes filter
nbf = NBFilter(targetcountry='mexico')
filtered_tw = nbf.filter_one_file(r'2012-07-04.json')

print "# NB filtered: %d" % len(filtered_tw)

