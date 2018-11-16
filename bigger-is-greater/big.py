import sys

t = int(input())

for _ in range(t):
    w = input().strip()
    lastch = None
    print (len(w), w, file=sys.stderr)
    ans = False
    for i in range(len(w)-1,0,-1):
        if (w[i-1] < w[i]):
            j = i+w[i:].index(min([c for c in list(w[i:]) if c > w[i-1]]))
            print ('min remaining after pos {}, ch={}, minpos={}, minch={}'.format(i-1, w[i-1], j, w[j]), file=sys.stderr)
            ans = True
            print ('"{}"+"{}"+"{}"+"{}"+"{}"'.format(w[0:i-1], w[j], w[i-1], w[i:j], w[j+1:]), file=sys.stderr)
            neww = w[0:i-1]+w[j]+w[i-1]+w[i:j]+w[j+1:]
            print ('neww', neww, file=sys.stderr)
            minw = neww[0:i] + ''.join(sorted(list(neww[i:])))
            print ('minw', minw, file=sys.stderr)
            print (minw)
            break
    if not ans:
        print ('no answer')
    #sys.exit()
