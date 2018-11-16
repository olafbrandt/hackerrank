#!/bin/python3

import sys
from itertools import combinations
from collections import Counter

def pairskills(t,a,b):
    #print ('{} | {} = {} [{}]'.format(t[a], t[b], bin(int(t[a], 2) | int(t[b],2)), bin(int(t[a], 2) | int(t[b],2)).count('1')), file=sys.stderr)
    return (bin(int(t[a], 2) | int(t[b],2)).count('1'))
    
n,m = input().strip().split(' ')
n,m = [int(n),int(m)]
topic = []
topic_counts = []
for _ in range(n):
    topic_t = str(input().strip())
    topic.append(topic_t)
    topic_counts.append(topic_t.count('1'))
    
combs = list(combinations(list(range(len(topic))),2))
print (topic_counts, topic, combs, file=sys.stderr)
cc = Counter([pairskills(topic, *c) for c in combs])
max_skill = sorted(list(cc.items()), key=lambda x: x[0], reverse=True)[0]
print (max_skill, file=sys.stderr)
print ('{}\n{}'.format(max_skill[0], max_skill[1]))

