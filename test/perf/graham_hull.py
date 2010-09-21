# Compute a convex hull using Graham's scan
import itertools

def convex_hull(points):
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

def convex_hull2(points):
    points = sorted(tuple(p) for p in points)
    upper = []
    push_upper = upper.append
    pop_upper = upper.pop
    lower = []
    push_lower = lower.append
    pop_lower = lower.pop
    for p in points:
        while len(upper) > 1:
            v0 = upper[-2]
            v1 = upper[-1]
            if ((v1[0] - v0[0])*(p[1] - v0[1]) 
                - (p[0] - v0[0])*(v1[1] - v0[1]) >= 0.0):
                pop_upper()
            else:
                break
        push_upper(p)
        while len(lower) > 1:
            v0 = lower[-2]
            v1 = lower[-1]
            if ((v1[0] - v0[0])*(p[1] - v0[1]) 
                - (p[0] - v0[0])*(v1[1] - v0[1]) <= 0.0):
                pop_lower()
            else:
                break
        push_lower(p)
    return upper + lower[-2:0:-1]
