
#!/bin/python

import sys

s,t = raw_input().strip().split(' ')
s,t = [int(s),int(t)]
a,b = raw_input().strip().split(' ')
a,b = [int(a),int(b)]
m,n = raw_input().strip().split(' ')
m,n = [int(m),int(n)]
apple = map(int,raw_input().strip().split(' '))
orange = map(int,raw_input().strip().split(' '))

print (sum(list([1 if (x+a >= s and x+a <= t) else 0 for x in apple])))
print (sum(list([1 if (x+b >= s and x+b <= t) else 0 for x in orange])))