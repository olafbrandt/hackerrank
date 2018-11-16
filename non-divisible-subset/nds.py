import sys, itertools

(n, k) = list(map(int, input().split()))
nums = list(map(int, input().split()))


mods = {}
for n in nums:
    x = n % k
    mods[x] = mods.get(x,0) + 1

maxmods = []
maxsetsize = 0
if True:
    len0 = mods.get(0,0)
    maxsetsize += min(1, len0)
    print ('{}->{}'.format(0, len0), file=sys.stderr)

if (k % 2 == 0):    
    lenk2 = mods.get(k//2,0)
    maxsetsize += min(1, lenk2)
    print ('{}->{}'.format(k//2, lenk2), file=sys.stderr)

for i in range(1,(k+1)//2):
    leni = mods.get(i,0)
    lenki = mods.get(k-i,0)
    print ('{}->{}, {}->{}'.format(i, leni, k-i, lenki), file=sys.stderr)
    if leni > lenki:
        maxmods += [i]
        maxsetsize += leni
    elif lenki > 0:
        maxmods += [k-i]
        maxsetsize += lenki
print(maxmods, file=sys.stderr)
print(maxsetsize, file=sys.stderr)
print (maxsetsize)
    
