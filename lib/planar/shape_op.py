"""Shape to shape comparison operations"""

import planar

def bbox_encloses_bbox(bbox_a, bbox_b):
    """Return True if bbox_a completely encloses bbox_b"""
    return (bbox_a.min.x <= bbox_b.min.x and
            bbox_a.min.y <= bbox_b.min.y and
            bbox_a.max.x >= bbox_b.max.x and
            bbox_a.max.y >= bbox_b.max.y)

def bbox_collides_bbox(bbox_a, bbox_b):
    """Return True if bbox_a collides with bbox_b"""
    return (bbox_a.min.x < bbox_b.max.x and
            bbox_a.max.x >= bbox_b.min.x and
            bbox_a.min.y < bbox_b.max.y and
            bbox_a.max.y >= bbox_b.min.y)

def line_collides_bbox(line, bbox):
    """Return True if line collides with bbox. Note this will work
    for `Line`, `Ray`, and `LineSegment` objects.
    """
    return bbox.contains_point(line.project(bbox.center))

def intersect_bbox_bbox(bbox_a, bbox_b):
    """Return the BoundingBox which is the intersection of bbox_a and bbox_b.
    Return None if the boxes do not intersect
    """
    minx = max(bbox_a.min.x, bbox_b.min.x)
    miny = max(bbox_a.min.y, bbox_b.min.y)
    maxx = min(bbox_a.max.x, bbox_b.max.x)
    maxy = min(bbox_a.max.y, bbox_b.max.y)
    if (minx < maxx and miny < maxy):
        return planar.BoundingBox((minx, miny), (maxx, maxy))

def intersect_line_bbox(line, bbox):
    """Return the points where line intersects bbox as a sequence
    of zero, one, or two points.
    """
    if line.direction.x == 0.0: # vertical line
        x1 = x2 = line.offset
        y1 = bbox.min.y
        y2 = bbox.max.y
    elif line.direction.y == 0.0: # horizontal line
        y1 = y2 = line.offset
        x1 = bbox.min.x
        x2 = bbox.max.x
    else:
        p = line.normal * line.offset # point on line nearest origin
        slope = line.direction.x / line.direction.y
        y1 = bbox.min.y
        x1 = p.x + (y1 - p.y) * slope
        if x1 < bbox.min.x or x1 > bbox.max.x:
            # Misses low horizontal box segment, try left vertical
            x1 = bbox.min.x
            y1 = p.y + (x1 - p.x) / slope

        y2 = bbox.max.y
        x2 = p.x + (y2 - p.y) * slope
        if x2 < bbox.min.x or x2 > bbox.max.x:
            # Misses high horizontal box segment, try right vertical
            x2 = bbox.max.x
            y2 = p.y + (x2 - p.x) / slope

    if bbox.min.x <= x1 <= bbox.max.x and bbox.min.y <= y1 <= bbox.max.y:
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
