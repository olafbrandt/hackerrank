#!/usr/bin/python
import pprint
from collections import defaultdict

# read the dictionary file
fname = 'words.txt'
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
while True:
	w = raw_input('Anagram: ')
	if len(w) < 1: break
	print 'Matches:', anagram_dict.get(hash(w), '---')
