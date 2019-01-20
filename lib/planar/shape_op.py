"""Shape to shape comparison operations"""

import planar

def bbox_encloses_bbox(bbox_a, bbox_b):
    """Return True if bbox_a completely encloses bbox_b"""
    return (bbox_a.min_point.x <= bbox_b.min_point.x and
            bbox_a.min_point.y <= bbox_b.min_point.y and
            bbox_a.max_point.x >= bbox_b.max_point.x and
            bbox_a.max_point.y >= bbox_b.max_point.y)

def bbox_collides_bbox(bbox_a, bbox_b):
    """Return True if bbox_a collides with bbox_b"""
    return (bbox_a.min_point.x < bbox_b.max_point.x and
            bbox_a.max_point.x >= bbox_b.min_point.x and
            bbox_a.min_point.y < bbox_b.max_point.y and
            bbox_a.max_point.y >= bbox_b.min_point.y)

def line_collides_bbox(line, bbox):
    """Return True if line collides with bbox. Note this will work
    for `Line`, `Ray`, and `LineSegment` objects.
    """
    return bbox.contains_point(line.project(bbox.center))

def line_collides_polygon(line, poly):
    pass

def polygon_collides_polygon(poly_a, poly_b):
    # General algorithm
    # For radial polys use the max radius it to determine the minimum
    # separation and return False immediately if intersection is impossible.
    # with bounding shapes this could also work when bounding circles are
    # stored.
    #
    # If not radial Intersect bboxes, if sufficiently large do a bbox center in
    # poly test on both and short-circuit if this returns True, if
    # bbox is empty return False
    #
    # for convex to convex do a separating-axis test:
    # for each edge in a look for possible intersection with each edge in b
    # if a possible intersection is found, suspend checking and move on to
    # the next edge in a. If an edge is found with no possible intersections
    # (all points on b "outside" the axis defined by edge of a) return False
    # if all have possible intersections, iterate again resolving them.
    # If any actual intersection point is found return True. If None are found,
    # return a test of whether any vert of a is in b or vice versa (this indicates
    # enclosure). false indicates no intersection but orientation 
    # and proximity prevents this from being detected early.
    #
    # possible optimization for many-sided convex: Use a binary search to
    # determine the edges on each poly closest to the other's centroid or
    # nearest opposing poly edge, or within the bbox intersection. Use that as
    # the start point for the SAT test so that non-intersection can be
    # determined quickly because that is where it would likely occur.
    #
    # for non-convex:
    # Do a mass edge intersection test. If edge count is sufficiently high,
    # use a sort-and-sweep algorithm otherwise just test pairwise. Bail
    # on any intersection with True. The bbox intersection could be helpful
    # to reduce the edges needing checks using binary searches within the
    # sorted edges.
    # If no intersections are found test if any verts of each poly is inside
    # the other. Look for a way to reuse the sorted edge data.
    # sorted edged could be cached in each poly too, and merge sorted
    # here
    # it may be possible that performing a convex hull is actually quicker
    # for extremely complex polys and intersecting that first. However I
    # think this could be handled by implementing bounding shapes
    # that the application can populate rather than some heuristic, but
    # it may be worth testing this.
    #
    # Worst case overall is polys in very close proximity with large
    # overlapping bboxes that do not actually intersect.
    pass

def intersect_bbox_bbox(bbox_a, bbox_b):
    """Return the BoundingBox which is the intersection of bbox_a and bbox_b.
    Return None if the boxes do not intersect
    """
    minx = max(bbox_a.min_point.x, bbox_b.min_point.x)
    miny = max(bbox_a.min_point.y, bbox_b.min_point.y)
    maxx = min(bbox_a.max_point.x, bbox_b.max_point.x)
    maxy = min(bbox_a.max_point.y, bbox_b.max_point.y)
    if (minx < maxx and miny < maxy):
        return planar.BoundingBox((minx, miny), (maxx, maxy))

def intersect_line_bbox(line, bbox):
    """Return the points where line intersects bbox as a sequence
    of zero, one, or two points.
    """
    if line.direction.x == 0.0: # vertical line
        x1 = x2 = line.offset
        y1 = bbox.min_point.y
        y2 = bbox.max_point.y
    elif line.direction.y == 0.0: # horizontal line
        y1 = y2 = line.offset
        x1 = bbox.min_point.x
        x2 = bbox.max_point.x
    else:
        p = line.normal * line.offset # point on line nearest origin
        slope = line.direction.x / line.direction.y
        y1 = bbox.min_point.y
        x1 = p.x + (y1 - p.y) * slope
        if x1 < bbox.min_point.x or x1 > bbox.max_point.x:
            # Misses low horizontal box segment, try left vertical
            x1 = bbox.min_point.x
            y1 = p.y + (x1 - p.x) / slope

        y2 = bbox.max_point.y
        x2 = p.x + (y2 - p.y) * slope
        if x2 < bbox.min_point.x or x2 > bbox.max_point.x:
            # Misses high horizontal box segment, try right vertical
            x2 = bbox.max_point.x
            y2 = p.y + (x2 - p.x) / slope

    if (bbox.min_point.x <= x1 <= bbox.max_point.x and 
        bbox.min_point.y <= y1 <= bbox.max_point.y):
        # If one point intersects, both must
        if x1 == x2 and y1 == y2:
            return (planar.Vec2(x1, y2),)
        return planar.Vec2(x1, y1), planar.Vec2(x2, y2)
    else:
        return ()

def intersect_ray_bbox(ray, bbox):
    """Return the points where ray intersects bbox as a sequence
    of zero, one, or two points.
    """
    points = intersect_line_bbox(ray.line, bbox)
    return tuple(p for p in points if not ray.point_behind(p))
