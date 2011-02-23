Polygon Objects
===============

.. currentmodule:: planar

Polygons in ``planar`` are represented as a sequence of vertices. Each pair of vertices defines one edge of the polygon. The simplest polygon is the triangle, thus a :class:`planar.Polygon` must have at least three vertices. The vertices of a polygon are mutable, but the number of vertices is fixed, so you cannot insert new vertices into an existing polygon object.

There are a number of ways to construct polygons. The default constructor simply accepts an iterable containing points. These become the vertices of the resulting polygon in whatever order they are supplied::

	>>> from planar import Polygon
	>>> poly = Polygon([(0,-1), (2,0), (0,1), (-2,0)])

It is also easy to construct regular polygons. To do so, you supply the :method:`~planar.Polygon.regular` method with the number or vertices, radius value, and optionally a center point, and the angle of the first vertex::

	>>> from planar import Polygon
	>>> hexagon = Polygon.regular(6, radius=4, angle=30)
	>>> print(hexagon)
	Polygon([(3.4641, 2), (0, 4), (-3.4641, 2), (-3.4641, -2), (0, -4), (3.4641, -2)], is_convex=True)

The :method:`~planar.Polygon.star` method lets you create radial polygons with vertices that alternate between two radii from the center point::

	>>> from planar import Polygon
	>>> star = Polygon.star(4, 1, 4)
	>>> print(star)
	Polygon([(1, 0), (2.82843, 2.82843), (0, 1), (-2.82843, 2.82843), (-1, 0), (-2.82843, -2.82843), (0, -1), (2.82843, -2.82843)], is_convex=False, is_simple=True)

The first argument of :method:`~planar.Polygon.star` is the number of "peaks". The resulting polygon has twice this number of vertices.

Classifying Polygons
--------------------

Polygons are broadly classified into simple and non-simple, convex and non-convex. ``planar`` can compute the classification for any arbitrary polygon. The classification has consequences that affect the operations and algorithms that can be used with the polygon.

A simple polygon is not self-intersecting, that is no two edges of the polygon cross. Simple polygons have a more simply defined interior and exterior, and also have a centroid. Non-simple polygons can have extremely complex boundaries. The ``is_simple`` attribute of a polygon instance can be inspected to determine if the polygon is simple. This value can be costly to compute for very large polygons, so it is cached the first time it is accessed.

A convex polygon has the simplest boundary topology. For any two points inside a convex shape, all points on the line between them are also inside. If you were to walk along the edges of a convex polygon, at each vertex you would always turn in the same direction. All convex polygons are also simple. The ``is_convex`` polygon attribute can be inspected to determine the convexity of a polygon object. This value is also cached to speed repeated access. Note that triangles are always both simple, and convex.

Many operations have very fast algorithms for convex polygons, so ``planar`` will often compute this attribute itself to select the best algorithm. If you supply a sequence of vertices when constructing a polygon that you know are already simple, or convex, you can declare this in the constructor to save calculations later. Be sure you declare these classifications correctly, however, or you may get incorrect results when using the polygon. When in doubt, let ``planar`` determine these values for you.

