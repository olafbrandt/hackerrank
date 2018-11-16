
def splitsum(x, sqr):
    sqr = str(sqr)
    result = False
    for i in range(len(sqr)+1):
        l = int('0'+sqr[:i])
        r = int('0'+sqr[i:])
        #print ('{}: {}+{}={} =? {}'.format(sqr, int('0'+sqr[:i]), int('0'+sqr[i:]), int('0'+sqr[:i]) + int('0'+sqr[i:]), x))
        if (x == int(sqr)):
            result = True
        elif (l != 0 and r != 0 and l+r==x):
            result = True
    return (result)

p = int(input())
q = int(input())
kaprekar = []
for x in range(p, q+1):
    if (splitsum(x, x*x)):
        kaprekar.append(x)
if (len(kaprekar)):
    print (*kaprekar)
else:
    print ("INVALID RANGE")

