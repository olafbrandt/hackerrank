
def answer(l):
	s0 = []
	s1 = []
	s2 = []

	for n in l:
		if n % 3 == 0:
			s0.insert(0, n)
		if n % 3 == 1:
			s1.insert(0, n)
		if n % 3 == 2:
			s2.insert(0, n)
	s0 = sorted(s0, reverse=True)
	s1 = sorted(s1, reverse=True)
	s2 = sorted(s2, reverse=True)

	x0 = len(s0)
	x1 = len(s1)
	x2 = len(s2)

	n0 = x0
	n1 = max (x1-1,0) // 3 * 3
	n2 = max (x2-1,0) // 3 * 3

	#print ('0: {}, {}, {}'.format(n0, s0[:n0], s0[n0:]))
	#print ('1: {}, {}, {}'.format(n1, s1[:n1], s1[n1:]))
	#print ('2: {}, {}, {}'.format(n2, s2[:n2], s2[n2:]))

	x0 -= n0
	x1 -= n1
	x2 -= n2

	d = max(x1, x2) - min(x1, x2)
	assert (d <= 3)

	if (d <= 1):
		m = min(x1, x2)
		n1 += m
		n2 += m
		x1 -= m
		x2 -= m
	elif (x1 == 3):
		n1 += 3
		x1 -= 3
	elif (x2 == 3):
		n2 += 3
		x2 -= 3

	#print()
	#print ('0: {}, {}, {}'.format(n0, s0[:n0], s0[n0:]))
	#print ('1: {}, {}, {}'.format(n1, s1[:n1], s1[n1:]))
	#print ('2: {}, {}, {}'.format(n2, s2[:n2], s2[n2:]))

	res = s0[0:n0] + s1[0:n1] + s2[0:n2]
	res = sorted(res, reverse=True)
	resnum = 0
	if (len(res)):
		resnum = int(''.join(map(str,res)))

	#print ('R: len={} {}'.format(len(res), resnum))

	return (resnum)