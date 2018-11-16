#!/bin/python3

import sys
import time
import bisect
    
if __name__ == "__main__":
    n = int(input().strip())
    scores = list(map(int, input().strip().split(' ')))
    m = int(input().strip())
    alice = list(map(int, input().strip().split(' ')))

    ascore = 0
    sortedset = list(sorted(set(scores)))
    
    for i in range(m):
        print (len(sortedset) - bisect.bisect_right(sortedset, alice[i]) + 1)
