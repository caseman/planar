from random import random, randint
from timeit import timeit
from planar import Vec2
from planar.c import Polygon

def rand_pt(span=10):
	return Vec2(random() * span - 0, random() * span - 0.5)

def rand_y_mono(vert_count):
	while 1:
		v1 = rand_pt()
		v2 = rand_pt()
		d = v1 - v2
		if abs(d.x) < abs(d.y) and abs(d.y) >= 1:
			if v2.y < v1.y:
				max_v = v1
				min_v = v2
			else:
				max_v = v2
				min_v = v1
			break
	left_x = min(min_v.x, max_v.x)
	right_x = max(min_v.x, max_v.x)
	height = max_v.y - min_v.y
	left = []
	right = []
	for i in range(vert_count - 2):
		if random() >= 0.5:
			left.append(Vec2(left_x - random() * 5, random() * height + min_v.y))
		else:
			right.append(Vec2(right_x + random() * 5, random() * height + min_v.y))
	left.sort(key=lambda v: v[1])
	right.sort(key=lambda v: v[1])
	pl1 = [(y, x) for x, y in [min_v] + left + [max_v]]
	pl2 = [(y, x) for x, y in [min_v] + right + [max_v]]
	if random() >= 0.5:
		right.reverse()
		verts = [min_v] + left + [max_v] + right
	else:
		left.reverse()
		verts = [min_v] + right + [max_v] + left
	first_i = randint(0, vert_count - 1)
	if first_i:
		verts = verts[first_i:] + verts[:first_i]
	assert len(verts) == vert_count, (len(verts), vert_count)
	poly = Polygon(verts)
	#poly._split_y_polylines()
	#assert poly._y_polylines == (pl1, pl2), (poly._y_polylines, (pl1, pl2))
	return poly

pts = [rand_pt(10) for i in range(2000)]

def poly_ymono_test(poly):
	def test():
		ymono_test = poly._pnp_y_monotone_test
		for pt in pts:
			ymono_test(pt)
	return test

def poly_winding_test(poly):
	def test():
		winding_test = poly._pnp_winding_test
		for pt in pts:
			winding_test(pt)
	return test

for verts in [4, 5, 6, 7, 8, 9, 10, 20, 40, 80, 160, 320, 640, 1280, 3000]:
	poly = rand_y_mono(verts)
	winding_test = poly._pnp_winding_test
	ymono_test = poly._pnp_y_monotone_test
	ins = 0
	for pt in pts:
		winding = winding_test(pt)
		ymono = ymono_test(pt)
		assert winding == ymono, (winding, ymono, pt, list(poly))
		ins += ymono
	print()
	print("ins", ins, "outs", len(pts)-ins)
	print(verts, "sided winding:", timeit(poly_winding_test(poly), number=100))
	print(verts, "sided y-mono:", timeit(poly_ymono_test(poly), number=100))

