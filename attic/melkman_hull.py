import itertools
import collections

def _melkman_hull(points):
    """Compute a convex hull from points arranged in a simple polyline using
    Melkman's algorithm. Return the points of the hull as a radial sequence.
    """
    def is_left(a, b, c):
        return ((b[0] - a[0])*(c[1] - a[1]) 
            - (c[0] - a[0])*(b[1] - a[1]) > 0.0)
    points = iter(points)
    a, b, c = itertools.islice(points, 3)
    if is_left(a, b, c):
        hull = collections.deque((c, a, b, c))
    else:
        hull = collections.deque((c, b, a, c))
    for p in points:
        if (not is_left(hull[-2], hull[-1], p) 
            or not is_left(p, hull[0], hull[1])):
            while len(hull) >= 2 and not is_left(hull[-2], hull[-1], p):
                hull.pop()
            hull.append(p)
            while len(hull) >= 2 and not is_left(p, hull[0], hull[1]):
                hull.popleft()
            hull.appendleft(p)
    hull.popleft()
    return hull

def _melkman_hull_opt(points):
    """Compute a convex hull from points arranged in a simple polyline using
    Melkman's algorithm. Return the points of the hull as a radial sequence.
    """
    points = iter(points)
    a, b, c = itertools.islice(points, 3)
    if ((b[0] - a[0])*(c[1] - a[1]) 
        - (c[0] - a[0])*(b[1] - a[1]) > 0.0):
        hull = collections.deque((c, a, b, c))
    else:
        hull = collections.deque((c, b, a, c))
    push = hull.append
    pushleft = hull.appendleft
    pop = hull.pop
    popleft = hull.popleft
    ends = c
    head = hull[1]
    tail = hull[-2]
    for p in points:
        tail_not_convex = ((ends[0] - tail[0])*(p[1] - tail[1])
            - (p[0] - tail[0])*(ends[1] - tail[1]) <= 0.0)
        head_not_convex = ((ends[0] - p[0])*(head[1] - p[1])
            - (head[0] - p[0])*(ends[1] - p[1]) <= 0.0)
        if tail_not_convex or head_not_convex:
            while tail_not_convex:
                pop()
                ends = tail
                tail = hull[-2]
                tail_not_convex = ((ends[0] - tail[0])*(p[1] - tail[1]) 
                    - (p[0] - tail[0])*(ends[1] - tail[1]) <= 0.0)
            push(p)
            while head_not_convex:
                popleft()
                ends = head
                head = hull[1]
                head_not_convex = ((ends[0] - p[0])*(head[1] - p[1])
                    - (head[0] - p[0])*(ends[1] - p[1]) <= 0.0)
            pushleft(p)
            ends = p
            head = hull[1]
            tail = hull[-2]
    popleft()
    return hull

