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

def pp_word_list(wl):
	max_len = max([len(x) for x in wl])
	wpl = (80-4) // (max_len+2)
	i = 0
	while (i < len(wl)):
		print('    ', end='')
		for j in range(wpl):
			if ((i+j) < len(wl)):
				print ('{:{w}s}  '.format(wl[i+j], w=max_len), end='')
		i += wpl
		print('')

#run the solving service
try:
	while True:
		w = input('Pangram: ').strip()
		if len(w) < 1: break
		h = hashu(w)
		hset = set(h)
		hset.remove(w[0])
		print ('{} --> [{}],{}'.format(w, w[0], ','.join(hset)))
		pangrams = []
		subpans = []
		for e in pangram_dict.items():
			if (set(e[0]) <= set(h)) and (w[0] in e[0]):
				if (len(set(e[0])) >= len(h)):
					pangrams.extend(e[1])
				else:
					subpans.extend(e[1])

		print('Pangrams:')
		pp_word_list(sorted(pangrams))
		print('Others:')
		pp_word_list(sorted(subpans))
except EOFError:
	pass

print()