from random import randint

def factorize(x):
	facts = [1]
	for d in range(2,int(x**0.5)+1):
		if x%d == 0:
			p = x//d
			if (p != d):
				facts += [d, x//d]
			else:
				facts += [p]
	return (facts)

def answer(l):
	posmap = {}
	facmap = {}
	dblcnt = {}
	tplcnt = {}
	triplecount = 0
	for p in range(len(l)):
		n = l[p]
		#print ('pos #{}: l={}, posmap = {}, facmap={}'.format(p, l[:p+1], posmap, facmap))

		facts = factorize(n)
		for f in facts:
			if f in posmap:
				for p2 in posmap[f]:
					for p3 in facmap.get(p2,[]):
						print ('triple: ({},{},{}) indicies:({},{},{})'.format(l[p3], l[p2], l[p], p3, p2, p))
						triplecount += 1
					facmap[p] = facmap.get(p, []) + [p2]

		posmap[l[p]] = posmap.get(l[p],[]) + [p]
	return (triplecount)

codes = [1, 1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 5]
codes = list(range(1,20+1))
#codes = [1, 1, 1]

if True:
	codes = []
	for _ in range(2000):
		codes += [randint(1,99)]
print ('answer: {} --> {}'.format(codes, answer(codes)))
