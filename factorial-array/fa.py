#!/bin/python3

import sys, time

factDict = {}

def factb(x):
    if x not in factDict:
        if (x > 40):
            return 0
        if x < 2:
            factDict[x] = 1
        else:
            factDict[x] = (x * factb(x-1)) % 10**9
    return factDict[x]

# Given l, r, increase the values at all indices between l and r (inclusive) by 1.
def op1(a, l, r):
    #print('op1', l, r, file=sys.stderr)
    #print('{}+{}+{}'.format(a[:l-1], list(map(lambda x: x+1, a[l-1:r])), a[r:]), file=sys.stderr)
    a = a[:l-1]+list(map(lambda x: x+1, a[l-1:r]))+a[r:]
    return a

#Given l, r, compute the sum of  for all  from l to r, inclusive. Print this value modulo 10**9.
def op2(a, l, r):
    #print('op2', l, r, file=sys.stderr)
    b = a[l-1:r]
    s = sum([factb(x) for x in b])
    s = s % 10**9
    #print (s, file=sys.stderr)
    print (s)

def op3(a, i, v):
    #print('op3', i, v, file=sys.stderr)
    a[i-1] = v
    return a    

if __name__ == "__main__":
    n, m = input().strip().split(' ')
    n, m = [int(n), int(m)]
    A = list(map(int, input().strip().split(' ')))
    for a0 in range(m):
        tsa = time.time()
        cmd = list(map(int, input().strip().split(' ')))
        if cmd[0] == 1:
            A = op1(A, cmd[1], cmd[2])
        elif cmd[0] == 2:
            op2(A, cmd[1], cmd[2])
        elif cmd[0] == 3:
            A = op3(A, cmd[1], cmd[2])
        tsb = time.time()
        print ('cmd={}, time={}'.format(cmd[0], int((tsb-tsa)*1000)),file=sys.stderr)


