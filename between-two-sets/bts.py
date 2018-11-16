#!/bin/python3

import sys
from collections import Counter
from itertools import combinations
from functools import reduce
import operator

def isprime(x):
    for d in range(2,int(x**0.5)+1):
        if x%d == 0: return False
    return True

def factorize(x):
    for d in range(2,int(x**0.5)+1):
        if x%d == 0:
            return (list(sorted([1]+[d, *factorize(x//d)])))
    return [1,x]

def getTotalX(a, b):
    #[print(n, factorize(n)) for n in range(26)]
    #sys.exit(0)

    sb = Counter(factorize(b[0]))
    print ('B:', b[0], sb, file=sys.stderr)
    for v in b[1:]:
        sb &= Counter(factorize(v))
        print ('B[]:', v, Counter(factorize(v)), sb, file=sys.stderr)

    sa = Counter(factorize(a[0]))
    print ('A:', a[0], sa, file=sys.stderr)
    for v in a[1:]:
        sa |= Counter(factorize(v))
        print ('A[]:', v, Counter(factorize(v)), sa, file=sys.stderr)
    
    #sb.subtract(sa)
    sb = sa & sb
    print ('sb', sb, file=sys.stderr)
    sx = +sb
    print ('sx', sx, file=sys.stderr)
    sxl = list(sx.elements())
    print ('sxl', sxl, file=sys.stderr)
    facts = []
    for r in range(1,len(sxl)+1):
        s = set(tuple(sorted(x)) for x in combinations(sxl, r))
        ms = [reduce(operator.mul, x, 1) for x in s]
        facts.extend(ms)
        print ('combinations:', r, s, ms, file=sys.stderr)
    facts = sorted(facts)
    print ('factors to both:', len(facts), facts, file=sys.stderr)

    if (len(sx) == 0):
        return (0)

    return (len(facts))

if __name__ == "__main__":
    n, m = input().strip().split(' ')
    n, m = [int(n), int(m)]
    a = list(map(int, input().strip().split(' ')))
    b = list(map(int, input().strip().split(' ')))
    total = getTotalX(a, b)
    print(total)


