from random import random, randint
from timeit import timeit
from planar import Vec2
from planar.polygon import Polygon

times = 500

def rand_pt(span=10):
	return Vec2(random() * span - 0, random() * span - 0.5)

pts = [Vec2(i, random() * 10.0 + 5.001) for i in range(359)]

for sides in [4, 5, 6, 7, 8, 9, 10, 20, 40, 80, 160, 320, 640]:
	angles = sorted(set(random() * 360.0 for i in range(sides)))
	if random() > 0.5:
		angles.reverse()
	poly = Polygon((Vec2.polar(a, 5) for a in angles))
	assert poly.is_convex

	tangents = poly._pt_tangents
	cvx_tangents = poly.tangents_to_point
	for pt in pts:
		assert not poly.contains_point(pt)
		tans = tangents(pt)
		cvx_tans = cvx_tangents(pt)
		assert tans == cvx_tans, (tans, cvx_tans, sides, pt, list(poly))
	
	def null():
		pt_tangents = poly._pt_tangents
		for pt in pts:
			pass
	
	null_time = timeit(null, number=times)
	
	def general_tangents():
		pt_tangents = poly._pt_tangents
		for pt in pts:
			pt_tangents(pt)
	
	print()
	print("General tangents", len(poly), "sides:", 
		timeit(general_tangents, number=times) - null_time)
	
	def convex_tangents():
		pt_tangents = poly.tangents_to_point
		for pt in pts:
			pt_tangents(pt)
	
	print("Convex tangents", len(poly), "sides:", 
		timeit(convex_tangents, number=times) - null_time)

	
