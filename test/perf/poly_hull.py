from random import random, randint
from timeit import timeit
import functools
from planar import Vec2, Vec2Array
from planar import polygon
from planar.polygon import Polygon
from nose.tools import assert_equal
import quick_hull
import graham_hull

def rand_pt(span=10):
	return Vec2(random() * span - 0.5, random() * span - 0.5)
def rand_pts(count, span=10):
	return [rand_pt(span) for i in range(count)]

times = 5000

def confirm_hull(points, hull):
	poly = Polygon(hull)
	assert poly.is_convex, (hull, graham_hull.convex_hull(points))
	return
	for pt in hull:
		if pt not in points:
			assert False, "Hull pt %r not in points" % pt
	for pt in points:
		if not poly.contains_point(pt) and pt not in hull:
			assert False, "Pt %r outside hull %r" % (pt, hull)

for i in range(100):
	rand = rand_pts(12)
	qhull = polygon._adaptive_quick_hull(rand)
	ghull = graham_hull.convex_hull(rand)
	confirm_hull(rand, qhull)
	confirm_hull(rand, ghull)
	assert Polygon(qhull) == Polygon(ghull), (qhull, ghull) 

for count in [4, 8, 16, 32, 64, 128, 256, 512, 1024]:
	rand = rand_pts(count)
	rand_tuples = [tuple(p) for p in rand]

	ghull = graham_hull.convex_hull(rand_tuples)
	confirm_hull(rand, ghull)
	qhull = quick_hull.convex_hull(rand)
	confirm_hull(rand, qhull)
	ahull = polygon._adaptive_quick_hull(rand)
	confirm_hull(rand, ahull)

	print("Graham rand", count, "points:", 
		timeit(functools.partial(graham_hull.convex_hull, rand_tuples),
		number=times))
	print("Quick rand", count, "points:", 
		timeit(functools.partial(quick_hull.convex_hull, rand),
		number=times))
	print("Adaptive rand", count, "points:", 
		timeit(functools.partial(polygon._adaptive_quick_hull, rand),
		number=times))
	
	reg = Polygon.regular(count, 10, center=(20,0))
	reg_tuples = [tuple(p) for p in reg]

	ghull = graham_hull.convex_hull(reg_tuples)
	confirm_hull(reg, ghull)
	qhull = quick_hull.convex_hull(reg)
	confirm_hull(reg, qhull)
	ahull = polygon._adaptive_quick_hull(reg)
	confirm_hull(reg, ahull)

	print("Graham reg", count, "points:", 
		timeit(functools.partial(graham_hull.convex_hull, reg_tuples),
		number=times))
	print("Quick reg", count, "points:", 
		timeit(functools.partial(quick_hull.convex_hull, reg),
		number=times))
	print("Adaptive reg", count, "points:", 
		timeit(functools.partial(polygon._adaptive_quick_hull, reg),
		number=times))
	
	mixed = reg_tuples + rand_tuples
	count = len(mixed)
	print("Graham mixed", count, "points:", 
		timeit(functools.partial(graham_hull.convex_hull, mixed),
		number=times))
	print("Quick mixed", count, "points:", 
		timeit(functools.partial(quick_hull.convex_hull, mixed),
		number=times))
	print("Adaptive mixed", count, "points:", 
		timeit(functools.partial(polygon._adaptive_quick_hull, mixed),
		number=times))
	
	multi = (list(Polygon.regular(count, 5, center=(0,8))) + 
		list(Polygon.regular(count, 3, center=(-2.5, -2.5))) +
		list(Polygon.regular(count, 10, center=(3,-5))))
	count = len(multi)
	print("Graham multi", count, "points:", 
		timeit(functools.partial(graham_hull.convex_hull, multi),
		number=times))
	print("Quick multi", count, "points:", 
		timeit(functools.partial(quick_hull.convex_hull, multi),
		number=times))
	print("Adaptive multi", count, "points:", 
		timeit(functools.partial(polygon._adaptive_quick_hull, multi),
		number=times))

	print()

