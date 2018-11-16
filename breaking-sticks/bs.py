#!/bin/python3

import sys
import random

def primesbelow(N):
    # http://stackoverflow.com/questions/2068372/fastest-way-to-list-all-primes-below-n-in-python/3035188#3035188
    #""" Input N>=6, Returns a list of primes, 2 <= p < N """
    correction = N % 6 > 1
    N = {0:N, 1:N-1, 2:N+4, 3:N+3, 4:N+2, 5:N+1}[N%6]
    sieve = [True] * (N // 3)
    sieve[0] = False
    for i in range(int(N ** .5) // 3 + 1):
        if sieve[i]:
            k = (3 * i + 1) | 1
            sieve[k*k // 3::2*k] = [False] * ((N//6 - (k*k)//6 - 1)//k + 1)
            sieve[(k*k + 4*k - 2*k*(i%2)) // 3::2*k] = [False] * ((N // 6 - (k*k + 4*k - 2*k*(i%2))//6 - 1) // k + 1)
    return [2, 3] + [(3 * i + 1) | 1 for i in range(1, N//3 - correction) if sieve[i]]

smallprimeset = set(primesbelow(100000))
_smallprimeset = 100000
def isprime(n, precision=7):
    # http://en.wikipedia.org/wiki/Miller-Rabin_primality_test#Algorithm_and_running_time
    if n < 1:
        raise ValueError("Out of bounds, first argument must be > 0")
    elif n <= 3:
        return n >= 2
    elif n % 2 == 0:
        return False
    elif n < _smallprimeset:
        return n in smallprimeset


    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1

    for repeat in range(precision):
        a = random.randrange(2, n - 2)
        x = pow(a, d, n)

        if x == 1 or x == n - 1: continue

        for r in range(s - 1):
            x = pow(x, 2, n)
            if x == 1: return False
            if x == n - 1: break
        else: return False

    return True

def gcd(x):
    g = x
    for i in range(2, int(x**0.5)+1):
        if (x % i == 0):
            g = min(g, i, x//i)
    return (g)

pf_dict = {}

def primefactors(x):
    factors = []
    print ('primefactors', x, file=sys.stderr)
    for i in range(2, int(x**0.5)+1):
        if (x % i == 0):
            result = list([i]+primefactors(x//i))
            return result
    result = [x]
    return result

def pollard_brent(n):
    if n % 2 == 0: return 2
    if n % 3 == 0: return 3

    y, c, m = random.randint(1, n-1), random.randint(1, n-1), random.randint(1, n-1)
    g, r, q = 1, 1, 1
    while g == 1:
        x = y
        for i in range(r):
            y = (pow(y, 2, n) + c) % n

        k = 0
        while k < r and g==1:
            ys = y
            for i in range(min(m, r-k)):
                y = (pow(y, 2, n) + c) % n
                q = q * abs(x-y) % n
            g = gcd(q, n)
            k += m
        r *= 2
    if g == n:
        while True:
            ys = (pow(ys, 2, n) + c) % n
            g = gcd(abs(x - ys), n)
            if g > 1:
                break

    return g

smallprimes = primesbelow(10**6)
def primefactorsfast(n, sort=False):
    factors = []

    for checker in smallprimes:
        while n % checker == 0:
            factors.append(checker)
            n //= checker
        if checker > n: break

    if n < 2: return factors

    while n > 1:
        if isprime(n):
            factors.append(n)
            break
        factor = pollard_brent(n) # trial division did not fully factor, switch to pollard-brent
        factors.extend(primefactors(factor)) # recurse to factor the not necessarily prime factor returned by pollard-brent
        n //= factor

    if sort: factors.sort()

    return factors

if __name__ == "__main__":
    n = int(input().strip())
    a = list(map(int, input().strip().split(' ')))
    results = []
    for x in a:
        factors = sorted(primefactorsfast(x), reverse=True)
        print ('{} --> {}'.format(x, factors), file=sys.stderr)
        width = 1
        moves = 0
        if (x > 1):
            for f in factors:
                moves += width
                #print ('{:5}     {}'.format(moves, (str(x//width)+' ')*width), file=sys.stderr)
                width = width * f
        moves += width
        #print ('{:5}     {}'.format(moves, '1 '*width), file=sys.stderr)
        results.append(moves)
    print (results, file=sys.stderr)
    print(sum(results))

