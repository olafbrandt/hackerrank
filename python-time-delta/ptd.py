#!/bin/python3

import sys
#import datetime, time
from datetime import datetime
import time

def time_delta(t1, t2):
    fmt = '%a %d %b %Y %H:%M:%S %z'
    dt1 = datetime.strptime(t1, fmt)
    dt2 = datetime.strptime(t2, fmt)
    return (abs(int((dt1 - dt2).total_seconds())))

if __name__ == "__main__":
    t = int(input().strip())
    for a0 in range(t):
        t1 = input().strip()
        t2 = input().strip()
        delta = time_delta(t1, t2)
        print(delta)
