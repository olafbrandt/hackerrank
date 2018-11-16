#!/bin/python3

import sys

n,m = input().strip().split(' ')
n,m = [int(n),int(m)]
c = [int(c_temp) for c_temp in input().strip().split(' ')]

def fn(x):
    if x != '-':
        x = x % 36
        if (x < 10):
            x = chr(ord('0')+x)
        else:
            x = chr(ord('a')+x-10)
    return (x)

distance = 0
frontier = []
virgin = {}
cities = {}
for i in range(n):
    cities[i] = '-'
    virgin[i] = 1
for i in c:
    frontier.append(i)
while (len(frontier)):
    next_frontier = []
    for i in frontier:
        assert cities[i] == '-' or cities[i] <= distance
        if cities[i] != '-':
            continue
        cities[i] = distance
        del virgin[i]
        if (i > 0) and (cities[i-1] == '-'):
            next_frontier.append(i-1)
        if (i < n-1) and (cities[i+1] == '-'):
            next_frontier.append(i+1)
    #print ('{:2} {}'.format(len(virgin.keys()), ''.join(map(fn, cities.values()))), file=sys.stderr)
    #print ('{:5}'.format(len(virgin.keys())), file=sys.stderr)
    if (len(virgin.keys()) == 0):
        break
    frontier = next_frontier
    distance += 1
print(distance)
