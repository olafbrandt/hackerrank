def answer(x,y):
	diag = x+y-1
	d1 = (diag-1) * diag // 2 + 1
	dx = d1 + x-1
	return (dx)