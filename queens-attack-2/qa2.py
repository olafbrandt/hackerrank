#!/bin/python3

import sys
n,k = input().strip().split(' ')
n,k = [int(n),int(k)]
rQueen,cQueen = input().strip().split(' ')
rQueen,cQueen = [int(rQueen),int(cQueen)]

rad = [0]*8
rad[0] = n-cQueen
rad[2] = n-rQueen
rad[4] = cQueen-1
rad[6] = rQueen-1
rad[1] = min(rad[0], rad[2])
rad[3] = min(rad[2], rad[4])
rad[5] = min(rad[4], rad[6])
rad[7] = min(rad[6], rad[0])

print (sum(rad), rad, file=sys.stderr)

for a0 in range(k):
    rObstacle,cObstacle = input().strip().split(' ')
    rObstacle,cObstacle = [int(rObstacle),int(cObstacle)]
    
    dc = cQueen - cObstacle
    dr = rQueen - rObstacle
    
    if (dc < 0) and (dr == 0):
        print ('rad[{}]: min({},{}) --> {}'.format(0, rad[0], -dc-1, min(rad[0], -dc-1)), file=sys.stderr)
        rad[0] = min(rad[0], -dc-1)
    elif (dc == 0) and (dr < 0):
        print ('rad[{}]: min({},{}) --> {}'.format(2, rad[2], -dr-1, min(rad[2], -dr-1)), file=sys.stderr)
        rad[2] = min(rad[2], -dr-1)
    elif (dc > 0) and (dr == 0):
        print ('rad[{}]: min({},{}) --> {}'.format(4, rad[4],  dc-1, min(rad[4],  dc-1)), file=sys.stderr)
        rad[4] = min(rad[4], dc-1)
    elif (dc == 0) and (dr > 0):
        print ('rad[{}]: min({},{}) --> {}'.format(6, rad[6],  dr-1, min(rad[6],  dr-1)), file=sys.stderr)
        rad[6] = min(rad[6], dr-1)
    elif (dc == dr) and (dc < 0):
        print ('rad[{}]: min({},{}) --> {}'.format(1, rad[1], -dr-1, min(rad[1], -dr-1)), file=sys.stderr)
        rad[1] = min(rad[1], -dr-1)
    elif (dc == -dr) and (dc > 0):
        print ('rad[{}]: min({},{}) --> {}'.format(3, rad[3], -dr-1, min(rad[3], -dr-1)), file=sys.stderr)
        rad[3] = min(rad[3], -dr-1)
    elif (dc == dr) and (dc > 0):
        print ('rad[{}]: min({},{}) --> {}'.format(5, rad[5],  dr-1, min(rad[5],  dr-1)), file=sys.stderr)
        rad[5] = min(rad[5], dr-1)
    elif (dc == -dr) and (dc < 0):
        print ('rad[{}]: min({},{}) --> {}'.format(7, rad[7],  dr-1, min(rad[7],  dr-1)), file=sys.stderr)
        rad[7] = min(rad[7], dr-1)
    else:
        print ('miss', file=sys.stderr)

    print ('[{},{}]->[{},{}]: {}, {}'.format(cObstacle, rObstacle, dc, dr, sum(rad), rad), file=sys.stderr)
print (sum(rad))

