Event Description & Summoning Filter

This classification model extracts the Civil Unrest Event related tweets 
that are "Ongoing event descriptions" or "Summoning for events". 

Note:
1. The filter is country-based, thus the civil unrest event tweets for foreign countries will be filtered.
2. Few external packages are required, including:
	* liblinear
		available at:  
			Windows: http://www.lfd.uci.edu/~gohlke/pythonlibs/
			CentOS Linux: sudo yum install python-liblinear
	* sklearn / scikit-learn
		available at:
			Windows: http://www.lfd.uci.edu/~gohlke/pythonlibs/#scikit-learn
	* pyparsing
		available at: 
			Windows: http://www.lfd.uci.edu/~gohlke/pythonlibs/#pyparsing
	* kmethods
		my personal method collection for convience
		available at github repo
		
3. check main_sample.py for examples.

---------------------------- Update ---------------------------------
1/27 First commit -- Current model only works for Mexico