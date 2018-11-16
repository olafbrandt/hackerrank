#!/bin/python3

'''
Prison Labor Dodgers
====================

Commander Lambda is all about efficiency, including using her bunny prisoners for manual labor. But no one's been properly
monitoring the labor shifts for a while, and they've gotten quite mixed up. You've been given the task of fixing them, but
after you wrote up new shifts, you realized that some prisoners had been transferred to a different block and aren't available
for their assigned shifts. And manually sorting through each shift list to compare against prisoner block lists will take
forever - remember, Commander Lambda loves efficiency!

Given two almost identical lists of prisoner IDs x and y where one of the lists contains an additional ID, write a function
answer(x, y) that compares the lists and returns the additional ID.

For example, given the lists x = [13, 5, 6, 2, 5] and y = [5, 2, 5, 13], the function answer(x, y) would return 6 because
the list x contains the integer 6 and the list y doesn't. Given the lists x = [14, 27, 1, 4, 2, 50, 3, 1] and
y = [2, 4, -4, 3, 1, 1, 14, 27, 50], the function answer(x, y) would return -4 because the list y contains the
integer -4 and the list x doesn't.

In each test case, the lists x and y will always contain n non-unique integers where n is at least 1 but never more than 99,
and one of the lists will contain an additional unique integer which should be returned by the function.  The same n non-unique
integers will be present on both lists, but they might appear in a different order, like in the examples above. Commander Lambda
likes to keep her numbers short, so every prisoner ID will be between -1000 and 1000.

Languages
=========

To provide a Python solution, edit solution.py
To provide a Java solution, edit solution.java

Test cases
==========

Inputs:
    (int list) x = [13, 5, 6, 2, 5]
    (int list) y = [5, 2, 5, 13]
Output:
    (int) 6

Inputs:
    (int list) x = [14, 27, 1, 4, 2, 50, 3, 1]
    (int list) y = [2, 4, -4, 3, 1, 1, 14, 27, 50]
Output:
    (int) -4
 '''

import sys
import timeit
from solution import answer_man, answer_set
from random import randint

try:
	x = []
	x = list(map(int, input().strip().split(' ')))
except:
	None

try:
	y = []
	y = list(map(int, input().strip().split(' ')))
except:
	None

def setupxy(size = 98):
	x = []
	y = []
	for i in range (size):
		x.append(randint(-1000,1000))
	temp = list(x);
	while (len(temp)):
		y.append(temp.pop(randint(0,len(temp)-1)))
	while True:
		val = randint(-1000,1000)
		if val not in y:
			y.insert(randint(0,len(y)-1), randint(-1000,1000))
			break
		else:
			print ('collision')
	return (x, y)


(x, y) = setupxy()
print (x, y)

if True:
	setup_code = '''
from solution import answer_man, answer_set
from random import randint
from __main__ import setupxy

(x,y) = setupxy()
'''	

	res = timeit.repeat(setup=setup_code, stmt='answer_man(x, y)', repeat=3, number=1000)
	print ('answer_man: timeit={}'.format(res))

	res = timeit.repeat(setup=setup_code, stmt='answer_set(x, y)', repeat=3, number=1000)
	print ('answer_set: timeit={}'.format(res))

#print ('answer manual: {}'.format(answer_man(x, y)))
#print ('answer set:    {}'.format(answer_set(x, y)))

