#!/bin/python3

import sys
import os
from math import log10, ceil


def  numberOfPairs_clean(a, k):
    matches = 0
    dictNums = {}

    for i in a:
        dictNums[i] = dictNums.get(i, 0) + 1
    
    while (dictNums):
        j, c = dictNums.popitem()
        
        if ((j + j == k) & (c >= 2)):
            matches += 1
        elif dictNums.get(k-j, 0) >= 1:
            matches += 1
            del dictNums[k-j]
    
    return matches  

def  numberOfPairs(a, k):
    matches = 0
    maxNum = k;
    dictNums = {}
    for i in a:
        dictNums[i] = dictNums.get(i, 0) + 1
        maxNum = i if i > maxNum else i

    dictSize = int(ceil(log10(len(dictNums))))
    numSize = int(ceil(log10(maxNum)))
    print ('Dict: {0:{1}d} unique entries'.format(len(dictNums), dictSize))
    
    while (dictNums):
        j, c = dictNums.popitem()
        
        if ((j + j == k) & (c >= 2)):
            matches += 1
            print ('Dict: {0:{5}d}. Match {1:{5}d}: {2:>-{6}d} + {3:<{6}d} = {4:<{6}d}'.format(len(dictNums), matches, j, j, k, dictSize, numSize))
        elif dictNums.get(k-j, 0) >= 1:
            matches += 1
            print ('Dict: {0:{5}d}. Match {1:{5}d}: {2:>-{6}d} + {3:<{6}d} = {4:<{6}d}'.format(len(dictNums), matches, j, k-j, k, dictSize, numSize))
            del dictNums[k-j]
#        else:
#            print ('Dict: {0:{1}d}. Delete {2:{3}d}'.format(len(dictNums), dictSize, j, numSize))
    
    print ('Matches: {0}'.format(matches))
    return matches  


#f = open(os.environ['OUTPUT_PATH'], 'w')
f = open('out.txt', 'w')

_a_cnt = 0
_a_cnt = int(input())
_a_i=0
_a = []
while _a_i < _a_cnt:
    _a_item = int(input());
    _a.append(_a_item)
    _a_i+=1


_k = int(input());

res = numberOfPairs(_a, _k);
f.write(str(res) + "\n")

f.close()
