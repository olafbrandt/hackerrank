#!/usr/bin/env python3

import pprint
from collections import defaultdict

# read the dictionary file
import os
filedir = os.path.dirname(os.path.abspath(__file__))
fname = filedir + '/' + 'words.txt'
with open(fname) as f:
    content = f.readlines()
content = [x.strip() for x in content]

# define the hash function
def hashu(w):
	return (''.join(sorted(set(w))))

def hash(w):
	return (''.join(sorted(list(w))))

# build the pangram solving dicionary
pangram_dict = defaultdict(list)
for w in content:
	h = hashu(w)
	if len(w) >= 4:
		pangram_dict[h].append(w)

#run the solving service
try:
	while True:
		w = input('Pangram: ')
		if len(w) < 1: break
		h = hashu(w)
		print ('{} --> {}'.format(w, ','.join(h)))
		pangrams = []
		subpans = []
		for e in pangram_dict.items():
			if (set(e[0]) <= set(h)) and (w[0] in e[0]):
				if (len(set(e[0])) >= len(h)):
					pangrams.extend(e[1])
				else:
					subpans.extend(e[1])
		print('Pangrams: {}'.format(sorted(pangrams)))
		print('Others:   {}'.format(sorted(subpans)))
except EOFError:
	pass

print()