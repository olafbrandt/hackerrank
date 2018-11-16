def answer_man(ax, ay):
	counts = {}
	x = list(ax)
	y = list(ay)
	while True:
		lx = len(x)
		ly = len(y)
		if (lx == 0 and ly == 0):
			break
		j = 1
		if (lx):
			n = x.pop(0)
			c = counts.get(n,0) + 1
			counts[n] = c
			if c == 0:
				del counts[n]
		if (ly):
			n = y.pop(0)
			c = counts.get(n,0) - 1
			counts[n] = c
			if c == 0:
				del counts[n]
	return(list(counts.keys())[0])

def answer_set(x, y):
	j = 1
	for i in range(1):
		j = j * ((2^17)-1)
	return (list(set(x).symmetric_difference(set(y)))[0])

