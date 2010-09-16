from timeit import timeit
from planar import Vec2
from planar.polygon import Polygon
from random import random
import itertools

def rand_pt(span=10):
	return Vec2(random() * span - 0.5, random() * span - 0.5)
def rand_pts(count, span=10):
	return [rand_pt(span) for i in range(count)]

polys = []

# Regular polygons
regulars = [Polygon.regular(i * 2 + 3, 10, angle=random() * 360.0)
	for i in range(20)]
stars = [Polygon.star(i + 2, 5, random() * 10, angle=random() * 360.0)
	for i in range(20)]
rands = [Polygon(rand_pts(i * 2 + 4)) for i in range(100)]

pts = [rand_pt(20) for i in range(20000)]
ins = 0

# confirm that the algorithms agree
for poly in itertools.chain(regulars, stars):
	crossing_test = poly._pnp_crossing_test
	winding_test = poly._pnp_winding_test
	contains_test = poly.contains_point
	for p in pts:
		cross = crossing_test(p)
		winding = winding_test(p)
		contains = contains_test(p)
		ins += winding
		assert cross == winding == contains, (
			list(poly), p, cross, winding, contains, poly._min_r, (p - poly.centroid).length, poly._max_r)

print("ins", ins)
print("outs", (len(regulars) + len(stars))*len(pts) - ins)

times = 10

def test_null():
	for poly in polys:
		crossing_test = poly._pnp_crossing_test
		for p in pts:
			pass

null = timeit(test_null, number=times)

def test_crossing(polys):
	def test():
		for poly in polys:
			crossing_test = poly._pnp_crossing_test
			for p in pts:
				crossing_test(p)
	return test

print("crossing regular", timeit(test_crossing(regulars), number=times) - null)
print("crossing stars", timeit(test_crossing(stars), number=times) - null)
print("crossing rands", timeit(test_crossing(rands), number=times) - null)

def test_winding(polys):
	def test():
		for poly in polys:
			winding_test = poly._pnp_winding_test
			for p in pts:
				winding_test(p)
	return test

print()
print("winding regular", timeit(test_winding(regulars), number=times) - null)
print("winding stars", timeit(test_winding(stars), number=times) - null)
print("winding rands", timeit(test_winding(rands), number=times) - null)


def test_contains(polys):
	def test():
		for poly in polys:
			contains_test = poly.contains_point
			for p in pts:
				contains_test(p)
	return test

print()
print("contains regular", timeit(test_contains(regulars), number=times) - null)
print("contains stars", timeit(test_contains(stars), number=times) - null)
print("contains rands", timeit(test_contains(rands), number=times) - null)

