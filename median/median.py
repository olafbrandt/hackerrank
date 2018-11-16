#!/bin/python

def partition2(ar, lo, hi, ip): 
    #print "part:", "lo:", lo, "hi:", hi, "pivot idx:", ip, "pivot val:", ar[ip]
    pivot = ar[ip]
    below = []
    equal = []
    above = []
    for i in range(lo, hi+1):
        if ar[i] < pivot:
            below.append(ar[i])
        elif ar[i] > pivot:
            above.append(ar[i])
        else:
            equal.append(ar[i])
    ar = list(below) + list(equal) + list(above)

    ip = len(below) if len(below) > ip else ip
    ip = len(below)+len(equal)-1 if len(below)+len(equal)-1 < ip else ip
    #print "done:", len(below), len(equal), len(above), ip, ar[ip]
    return (ar, ip)

def partition(ar, lo, hi, ip): 
    print "part:", "lo:", lo, "hi:", hi, "pivot idx:", ip, "pivot val:", ar[ip]
    pivot = ar[ip]
    iswap = lo
    for i in range(lo, hi+1):
        if (ar[i] < pivot):
            if (i != iswap):
                print iswap, "<-->", i, "::", ar[iswap], "<-->", ar[i], "ip:", ip
                ar[i], ar[iswap] =  ar[iswap], ar[i]
                if (ip == i): ip = iswap
                elif (ip == iswap): ip = i    
                #print iswap, "<-->", i, ": ", " ".join(map(str, ar)), "ip:", ip
                #print iswap, "<-->", i, ": ", "ip:", ip
            iswap += 1
    if ((ip != iswap) and (ar[ip] != ar[iswap])):
#    if (ip != iswap):
        print "last swap:", ip, "<-->", iswap, "::", ar[ip], "<-->", ar[iswap], "ip:", iswap
        ar[ip], ar[iswap] =  ar[iswap], ar[ip]
        #print ip, "<-->", iswap, "::", " ".join(map(str, ar)), "ip:", iswap
        ip = iswap
    else:
        print "no swap:", ip, "<-->", iswap, "::", ar[ip], "<-->", ar[iswap], "ip:", iswap        
    #print " ".join(map(str, ar)), "-->", lo, hi, ip, ar[ip]
    print  "-->", lo, hi, ip, ar[ip]
    return (ip)

def  quick_sort(ar, lo, hi):
    pivot = partition(ar, lo, hi, hi)
    if (pivot - lo >= 2):
        quick_sort(ar, lo, pivot - 1)
    if (hi - pivot >= 2):
        quick_sort(ar, pivot + 1, hi)
    
m = input()
ar = [int(i) for i in raw_input().strip().split()]
mid = len(ar)/2
cnt = 0;

#quick_sort(ar, 0, len(ar)-1)
#print " ".join(map(str, ar))

while True:
    ar, resmid = partition2(ar, 0, len(ar)-1, mid)
    #print "cnt:", cnt, "mid:", mid, "resmid:", resmid, "dif:", mid-resmid 
    for i in range(len(ar)):
        if (i <= resmid):
            if (ar[i] > ar[resmid]):
                print "low:", i, ar[i], ">", ar[resmid]
        if (i >= resmid):
            if (ar[i] < ar[resmid]):
                print "high:", i, ar[i], "<", ar[resmid]

    if (resmid == mid): break
    cnt += 1

print ar[mid]    
#print cnt, mid, len(ar), ":::", ar[mid-1], ar[mid], ar[mid+1]
