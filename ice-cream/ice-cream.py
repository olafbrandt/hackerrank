#!/bin/python3
import sys

t = int(raw_input().strip())
#print "t", t
for i in range(t):
    m = int(raw_input().strip())
    n = int(raw_input().strip())
    c = raw_input().strip().split(' ')
    c = [int(s) for s in c]
    dc = {}
    for j in range(len(c)):
        x = c[j]
        if x in dc:
            dc[x].extend([j])
        else:
            dc[x] = [j]
    #print dc
    a = 0
    b = 0
    for x in c:
        #print "test", x
        if (m - x) in dc:
            #print "found", x, "+", m-x, "=", m
            if ((x == (m-x)) and (len(dc[x]) > 1)):
                a,b = dc[x][0]+1, dc[x][1]+1
                break
            elif (x <> (m-x)):
                a,b = dc[x][0]+1, dc[m-x][0]+1
                #print dc[x], dc[n-x]
                break
    if (a == 0):
        print m, n, x, m - x, dc
    if (a > b):
        c = a
        a = b
        b = c
    print a, b