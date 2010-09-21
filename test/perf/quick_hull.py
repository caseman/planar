import planar

def convex_hull(points):
    """Compute the convex hull from an arbitrary collection of points
    using the quick hull algorithm. Return the points of the hull
    as a list in radial sequence.
    """
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
    partition_point = planar.Vec2(*partition_point)
    
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

