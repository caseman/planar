from timeit import timeit
from planar import Vec2
from planar.c import Polygon
from random import random
import itertools

def rand_pt(span=10):
	return Vec2(random() * span - 0.5, random() * span - 0.5)

tris = [Polygon([rand_pt(), rand_pt(), rand_pt()]) for i in range(100)]
pts = [rand_pt(20) for i in range(1000)]
ins = count = 0

# confirm the two algorithms agree
for tri in tris:
	winding_test = tri._pnp_winding_test
	bary_test = tri._pnp_triangle_test
	for p in pts:
		cross = winding_test(p)
		bary = bary_test(p)
		ins += bary
		count += 1
		assert cross == bary, (count, list(tri), p, cross, bary)

print("ins", ins)
print("outs", len(tris)*len(pts) - ins)

times = 10

def test_null():
	for tri in tris:
		winding_test = tri._pnp_winding_test
		for p in pts:
			pass

null = timeit(test_null, number=times)

def test_winding():
	for tri in tris:
		winding_test = tri._pnp_winding_test
		for p in pts:
			winding_test(p)

print("winding", timeit(test_winding, number=times) - null)

def test_bary():
	for tri in tris:
		bary_test = tri._pnp_triangle_test
		for p in pts:
			bary_test(p)

print("bary", timeit(test_bary, number=times) - null)

