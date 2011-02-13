from random import random, randint
from timeit import timeit
import functools
import itertools
from planar import Vec2, Vec2Array
from planar import polygon
from planar.c import Polygon
from nose.tools import assert_equal

def rand_pt(span=10):
    return Vec2(random() * span - 0.5, random() * span - 0.5)
def rand_pts(count, span=10):
    return [rand_pt(span) for i in range(count)]

def graham_hull(points):
    """Reference implementation of Graham's convex hull algorithm.
    This is actually a chain-hull, since it sorts the points
    lexicographically rather than by angle.
    """
    points = sorted(tuple(p) for p in points)
    upper = []
    push = upper.append
    pop = upper.pop
    for p in points:
        while len(upper) > 1:
            v0 = upper[-2]
            v1 = upper[-1]
            if ((v1[0] - v0[0])*(p[1] - v0[1]) 
                - (p[0] - v0[0])*(v1[1] - v0[1]) >= 0.0):
                pop()
            else:
                break
        push(p)
    lower = []
    push = lower.append
    pop = lower.pop
    for p in points[::-1]:
        while len(lower) > 1:
            v0 = lower[-2]
            v1 = lower[-1]
            if ((v1[0] - v0[0])*(p[1] - v0[1]) 
                - (p[0] - v0[0])*(v1[1] - v0[1]) >= 0.0):
                pop()
            else:
                break
        push(p)
    return upper + lower[1:-1]

def quick_hull(points):
    """Reference implementation of quickhull."""
    leftmost = rightmost = points[0]
    for p in points:
        if p[0] < leftmost[0]:
            leftmost = p
        elif p[0] > rightmost[0]:
            rightmost = p
    upper_points = set()
    lower_points = set()
    add_upper = upper_points.add
    add_lower = lower_points.add
    lx, ly = leftmost
    line_w = rightmost[0] - leftmost[0]
    line_h = rightmost[1] - leftmost[1]
    for p in points:
        if line_w * (p[1] - ly) - (p[0] - lx) * line_h > 0.0:
            add_upper(p)
        else:
            add_lower(p)
    upper_points.discard(leftmost)
    upper_points.discard(rightmost)
    lower_points.discard(leftmost)
    lower_points.discard(rightmost)
    hull = []
    if upper_points:
        _qhull_partition(hull, upper_points, leftmost, rightmost)
    else:
        hull.append(leftmost)
    if lower_points:
        _qhull_partition(hull, lower_points, rightmost, leftmost)
    else:
        hull.append(rightmost)
    return hull

def _qhull_partition(hull, points, p0, p1):
    # Find point furthest from line p0->p1 as partition point
    furthest = -1.0
    p0_x, p0_y = p0
    pline_dx = p1[0] - p0[0]
    pline_dy = p1[1] - p0[1]
    for p in points:
        dist = pline_dx * (p[1] - p0_y) - (p[0] - p0_x) * pline_dy
        if dist > furthest:
            furthest = dist
            partition_point = p
    partition_point = Vec2(*partition_point)
    
    # Compute the triangle partition_point->p0->p1
    # in barycentric coordinates
    # All points inside this triangle are not in the hull
    # divide the remaining points into left and right sets
    left_points = []
    right_points = []
    add_left = left_points.append
    add_right = right_points.append
    v0 = p0 - partition_point
    v1 = p1 - partition_point
    dot00 = v0.length2
    dot01 = v0.dot(v1)
    dot11 = v1.length2
    inv_denom = 1.0 / (dot00 * dot11 - dot01 * dot01)
    for p in points:
        v2 = p - partition_point
        dot02 = v0.dot(v2)
        dot12 = v1.dot(v2)
        u = (dot11 * dot02 - dot01 * dot12) * inv_denom
        v = (dot00 * dot12 - dot01 * dot02) * inv_denom
        # Since the partition point is the furthest from p0->p1
        # u and v cannot both be negative
        # Note the partition point is discarded here
        if v < 0.0:
            add_left(p)
        elif u < 0.0:
            add_right(p)

    if len(left_points) > 1:
        _qhull_partition(hull, left_points, p0, partition_point)
    else:
        # Trivial partition
        hull.append(p0)
        hull.extend(left_points)

    if len(right_points) > 1:
        _qhull_partition(hull, right_points, partition_point, p1)
    else:
        # Trivial partition
        hull.append(partition_point)
        hull.extend(right_points)

times = 5000

def confirm_hull(points, hull):
    poly = Polygon(hull)
    assert poly.is_convex, (hull, graham_hull(points))
    return
    for pt in hull:
        if pt not in points:
            assert False, "Hull pt %r not in points" % pt
    for pt in points:
        if not poly.contains_point(pt) and pt not in hull:
            assert False, "Pt %r outside hull %r" % (pt, hull)

for i in range(100):
    rand = rand_pts(12)
    qhull = Polygon.convex_hull(rand)
    ghull = graham_hull(rand)
    confirm_hull(rand, qhull)
    confirm_hull(rand, ghull)
    assert Polygon(qhull) == Polygon(ghull), (qhull, ghull) 

for count in [4, 8, 16, 32, 64, 128, 256, 512, 1024]:
    rand = rand_pts(count)
    rand_tuples = [tuple(p) for p in rand]

    ghull = graham_hull(rand_tuples)
    confirm_hull(rand, ghull)
    qhull = quick_hull(rand)
    confirm_hull(rand, qhull)
    ahull = Polygon.convex_hull(rand)
    confirm_hull(rand, ahull)

    print("Graham rand", count, "points:", 
        timeit(functools.partial(graham_hull, rand_tuples),
        number=times))
    print("Quick rand", count, "points:", 
        timeit(functools.partial(quick_hull, rand),
        number=times))
    print("Adaptive rand", count, "points:", 
        timeit(functools.partial(Polygon.convex_hull, rand),
        number=times))
    
    reg = Polygon.regular(count, 10, center=(20,0))
    reg_tuples = [tuple(p) for p in reg]

    ghull = graham_hull(reg_tuples)
    confirm_hull(reg, ghull)
    qhull = quick_hull(reg)
    confirm_hull(reg, qhull)
    ahull = Polygon.convex_hull(reg)
    confirm_hull(reg, ahull)

    print("Graham reg", count, "points:", 
        timeit(functools.partial(graham_hull, reg_tuples),
        number=times))
    print("Quick reg", count, "points:", 
        timeit(functools.partial(quick_hull, reg),
        number=times))
    print("Adaptive reg", count, "points:", 
        timeit(functools.partial(Polygon.convex_hull, reg),
        number=times))
    
    mixed = reg_tuples + rand_tuples
    count = len(mixed)
    print("Graham mixed", count, "points:", 
        timeit(functools.partial(graham_hull, mixed),
        number=times))
    print("Quick mixed", count, "points:", 
        timeit(functools.partial(quick_hull, mixed),
        number=times))
    print("Adaptive mixed", count, "points:", 
        timeit(functools.partial(Polygon.convex_hull, mixed),
        number=times))
    
    multi = (list(Polygon.regular(count, 5, center=(0,8))) + 
        list(Polygon.regular(count, 3, center=(-2.5, -2.5))) +
        list(Polygon.regular(count, 10, center=(3,-5))))
    count = len(multi)
    print("Graham multi", count, "points:", 
        timeit(functools.partial(graham_hull, multi),
        number=times))
    print("Quick multi", count, "points:", 
        timeit(functools.partial(quick_hull, multi),
        number=times))
    print("Adaptive multi", count, "points:", 
        timeit(functools.partial(Polygon.convex_hull, multi),
        number=times))

    print()


