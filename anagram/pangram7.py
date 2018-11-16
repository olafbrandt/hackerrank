#!/usr/bin/python

import pprint
from collections import defaultdict

import sys
if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")

# read the dictionary file
import os
filedir = os.path.dirname(os.path.abspath(__file__))
fname = filedir + '/' + 'words.txt'
with open(fname) as f:
    content = f.readlines()
content = [x.strip() for x in content]

# define the hash function
def hash(w):
	return (''.join(sorted(list(w.lower()))))

# build the anagram solving dicionary
anagram_dict = defaultdict(list)
for w in content:
	anagram_dict[hash(w)].append(w)

#run the solving service
try:
	while True:
		w = input('Anagram: ')
		if len(w) < 1: break
		print ('Matches:', anagram_dict.get(hash(w), '---'))
except EOFError:
	pass

print()