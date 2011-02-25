"""Polygon class unit tests"""

from __future__ import division
import sys
import math
import unittest
from nose.tools import assert_equal, assert_almost_equal, raises


def assert_contains_point(polys, i, p):
    containing = [j for j, t in enumerate(polys) 
        if t.contains_point(p)]
    if i is not None:
        assert_equal([i], containing)
    else:
        assert_equal([], containing)


class PolygonBaseTestCase(object):

    @raises(TypeError)
    def test_too_few_args(self):
        self.Polygon()

    @raises(ValueError)
    def test_no_verts(self):
        self.Polygon([])

    @raises(ValueError)
    def test_too_few_verts(self):
        self.Polygon([(0,0), (1,1)])

    def test_init_triangle(self):
        poly = self.Polygon([(-1,0), (1,1), (0,0)])
        assert_equal(len(poly), 3)
        assert_equal(tuple(poly), 
            (self.Vec2(-1,0), self.Vec2(1,1), self.Vec2(0,0)))

    def test_is_Seq2_subclass(self):
        import planar
        assert issubclass(self.Polygon, planar.Seq2)
        poly = self.Polygon([(-1,0), (-1,1), (0,0), (0, -1)])
        assert isinstance(poly, planar.Seq2)

    def test_triangle_is_known_convex(self):
        poly = self.Polygon([(-1,0), (1,1), (0,0)])
        assert poly.is_convex_known
        assert poly.is_convex

    def test_triangle_is_known_simple(self):
        poly = self.Polygon([(-1,0), (1,1), (0,0)])
        assert poly.is_simple_known
        assert poly.is_simple

    def test_convex_not_known(self):
        poly = self.Polygon([(-1,0), (-1,1), (0,0), (0, -1)])
        assert_equal(len(poly), 4)
        assert not poly.is_convex_known

    def test_specify_convex(self):
        poly = self.Polygon([(-1,0), (-1,1), (0,0), (0, -1)], 
            is_convex=True)
        assert_equal(len(poly), 4)
        assert poly.is_convex_known
        assert poly.is_convex
        assert poly.is_simple_known
        assert poly.is_simple

    def test_triangle_is_always_convex(self):
        poly = self.Polygon([(-1,0), (1,1), (0,0)], is_convex=False)
        assert poly.is_convex_known
        assert poly.is_convex
        assert poly.is_simple_known
        assert poly.is_simple

    def test_specify_simple(self):
        poly = self.Polygon([(-1,0), (-0.5, 0.5), (-1,1), (0,0), (0, -1)], 
            is_simple=True)
        assert poly.is_simple_known
        assert poly.is_simple
        assert not poly.is_convex_known

    def test_is_convex(self):
        poly = self.Polygon([(-1,0), (-1,1), (0,0), (0, -1)])
        assert not poly.is_convex_known
        assert poly.is_convex
        assert poly.is_convex_known
        assert poly.is_convex # test cached value

    def test_not_is_convex(self):
        poly = self.Polygon([(0,0), (-1,1), (0,0.5), (-1, -1)])
        assert not poly.is_convex_known
        assert not poly.is_convex
        assert poly.is_convex_known
        assert not poly.is_convex # test cached value

    def test_convex_degenerate_cases(self):
        # Pentagram
        poly = self.Polygon([(-1,-1), (0,1), (1,-1), (-1,0), (1,0)])
        assert not poly.is_convex
        # Rect with backtracking vert along edge
        poly = self.Polygon([(0,0), (2,0), (1,0), (4,0), (4,-1), (0,-1)])
        assert not poly.is_convex
        # Rect with coincident edges
        poly = self.Polygon([(0,0), (0,1), (1,1), (1,0), 
            (0,0), (0,1), (1,1), (1,0)])
        assert not poly.is_convex
        # Triangle with coincident intruding edges
        poly = self.Polygon([(-2,0), (0,2), (-0.5,1), (0,2), (2,0)])
        assert not poly.is_convex

    def test_convex_is_simple(self):
        poly = self.Polygon([(-1,-1), (1,-1), (0.5,0), (0, 0)])
        assert not poly.is_simple_known
        assert poly.is_convex
        assert poly.is_simple_known
        assert poly.is_simple
        assert poly.is_simple # test cached value

    def test_non_convex_simple_unknown(self):
        poly = self.Polygon([(-1,-1), (1,-1), (1,0), (0, -0.9)])
        assert not poly.is_simple_known
        assert not poly.is_convex
        assert not poly.is_simple_known

    def test_is_simple(self):
        poly = self.Polygon([(0,0), (-1,-1), (-2, 0), (-1, 1)])
        assert not poly.is_simple_known
        assert poly.is_simple
        assert poly.is_simple_known
        assert poly.is_simple # test cached value

    def test_not_is_simple(self):
        poly = self.Polygon([(0,0), (-1,1), (1,1), (-1,0)])
        assert not poly.is_simple_known
        assert not poly.is_simple
        assert poly.is_simple_known
        assert not poly.is_simple # test cached value
    
    def test_mutation_invalidates_cached_properties(self):
        poly = self.Polygon([(0.5,0.5), (0.5,-0.5), (-0.5,-0.5), (-0.5,0.5)])
        assert poly.is_convex
        assert poly.is_simple
        assert poly.is_convex_known
        assert poly.is_simple_known
        poly[0] = (0, 0.6)
        assert not poly.is_convex_known
        assert not poly.is_simple_known
        assert poly.is_convex
        assert poly.is_simple
        assert poly.is_convex_known
        assert poly.is_simple_known
        poly[-1] = (0, 0)
        assert not poly.is_convex_known
        assert not poly.is_simple_known
        assert not poly.is_convex
        assert poly.is_simple
        assert poly.is_convex_known
        assert poly.is_simple_known
        poly[-1] = (1, 0)
        assert not poly.is_convex_known
        assert not poly.is_simple_known
        assert not poly.is_convex
        assert not poly.is_simple
        assert poly.is_convex_known
        assert poly.is_simple_known
        poly[0] = (0.5, 0.5)
        poly[1] = (0.5, -0.5)
        poly[2] = (-0.5, -0.5)
        poly[3] = (-0.5, 0.5)
        assert not poly.is_convex_known
        assert not poly.is_simple_known
        assert poly.is_convex
        assert poly.is_simple
        assert poly.is_convex_known
        assert poly.is_simple_known

    def test_regular(self):
        import planar
        poly = self.Polygon.regular(5, 1.5)
        assert isinstance(poly, self.Polygon)
        assert_equal(len(poly), 5)
        assert poly.is_convex_known
        assert poly.is_simple_known
        assert poly.is_centroid_known
        assert poly.is_convex
        assert poly.is_simple
        assert isinstance(poly.centroid, planar.Vec2)
        assert_equal(poly.centroid, (0, 0))
        angle = 0
        for i in range(5):
            assert_equal(self.Vec2.polar(angle, 1.5), poly[i])
            angle += 72

    def test_regular_with_center_and_angle(self):
        import planar
        angle = -60
        poly = self.Polygon.regular(vertex_count=3, radius=2, 
            center=(-3, 1), angle=angle)
        assert_equal(len(poly), 3)
        assert poly.is_convex_known
        assert poly.is_simple_known
        assert poly.is_centroid_known
        assert poly.is_convex
        assert poly.is_simple
        assert isinstance(poly.centroid, planar.Vec2)
        assert_equal(poly.centroid, (-3, 1))
        for i in range(3):
            assert_equal(self.Vec2.polar(angle, 2) + (-3, 1), poly[i])
            angle += 120

    @raises(ValueError)
    def test_regular_too_few_sides(self):
        self.Polygon.regular(2, 1)

    def test_star(self):
        import planar
        poly = self.Polygon.star(5, 3, 5)
        assert_equal(len(poly), 10)
        assert poly.is_convex_known
        assert poly.is_simple_known
        assert poly.is_centroid_known
        assert not poly.is_convex
        assert poly.is_simple
        assert isinstance(poly.centroid, planar.Vec2)
        assert_equal(poly.centroid, (0, 0))
        angle = 0
        for i in range(5):
            assert_equal(self.Vec2.polar(angle, 3), poly[i * 2])
            angle += 36
            assert_equal(self.Vec2.polar(angle, 5), poly[i * 2 + 1])
            angle += 36

    def test_star_is_convex_with_same_radii(self):
        import planar
        poly = self.Polygon.star(9, 2, 2)
        assert_equal(len(poly), 18)
        assert poly.is_convex_known
        assert poly.is_simple_known
        assert poly.is_centroid_known
        assert poly.is_convex
        assert poly.is_simple
        assert isinstance(poly.centroid, planar.Vec2)
        assert_equal(poly.centroid, (0, 0))

    def test_star_with_center_and_angle(self):
        import planar
        poly = self.Polygon.star(peak_count=2, radius1=1.5, radius2=3, 
            center=(-11, 3), angle=15)
        assert isinstance(poly, self.Polygon)
        assert_equal(len(poly), 4)
        assert poly.is_convex_known
        assert poly.is_simple_known
        assert poly.is_centroid_known
        assert not poly.is_convex
        assert poly.is_simple
        assert isinstance(poly.centroid, planar.Vec2)
        assert_equal(poly.centroid, (-11, 3))
        assert_equal(poly[0], self.Vec2.polar(15, 1.5) + (-11, 3))
        assert_equal(poly[1], self.Vec2.polar(105, 3) + (-11, 3))
        assert_equal(poly[2], self.Vec2.polar(195, 1.5) + (-11, 3))
        assert_equal(poly[3], self.Vec2.polar(285, 3) + (-11, 3))

    def test_star_with_one_negative_radius(self):
        import planar
        poly = self.Polygon.star(3, -1, 2)
        assert_equal(len(poly), 6)
        assert poly.is_convex_known
        assert not poly.is_simple_known
        assert not poly.is_centroid_known
        assert not poly.is_convex
        assert not poly.is_simple
        assert_equal(poly.centroid, None)

    @raises(ValueError)
    def test_star_too_few_peaks(self):
        self.Polygon.star(1, 1, 2)

    def test_centroid_convex(self):
        import planar
        poly = self.Polygon([(1, -2), (0, 0), (1, 0), (3, 0), (4, -2)])
        assert poly.is_convex
        assert not poly.is_centroid_known
        assert_equal(poly.centroid, (2, -1))
        assert isinstance(poly.centroid, planar.Vec2)
        assert poly.is_centroid_known
        assert_equal(poly.centroid, (2, -1)) # check cached value

    def test_centroid_concave(self):
        import planar
        poly = self.Polygon([(3,3), (1,-1), (-1,-1), (-3,3), (-1,-2), (1,-2)])
        assert not poly.is_convex
        assert poly.is_simple
        assert not poly.is_centroid_known
        assert_equal(poly.centroid, (0, -0.75))
        assert isinstance(poly.centroid, planar.Vec2)
        assert poly.is_centroid_known
        assert_equal(poly.centroid, (0, -0.75)) # check cached value

    def test_centroid_non_simple(self):
        poly = self.Polygon([(-1,1), (0,0), (1,1), (0,1), (0,-2)])
        assert not poly.is_centroid_known
        assert not poly.is_simple_known
        assert_equal(poly.centroid, None)
        assert poly.is_centroid_known
        assert_equal(poly.centroid, None)
        assert not poly.is_simple

    def test_bounding_box(self):
        import planar
        poly = self.Polygon([(1, -2), (0, 0), (1, 0), (3, 0), (4, -2)])
        bbox = poly.bounding_box
        assert isinstance(bbox, planar.BoundingBox)
        assert_equal(bbox.min_point, (0, -2))
        assert_equal(bbox.max_point, (4, 0))

    def test_eq_identical(self):
        poly1 = self.Polygon([(0,0), (1,0), (1,1), (-1, 1)])
        poly2 = self.Polygon([(0,0), (1,0), (1,1), (-1, 1)])
        assert poly1 == poly2
        assert not poly1 != poly2

    def test_eq_same_object(self):
        poly = self.Polygon([(-1,1), (0,0), (1,1), (0,1), (0,-2)])
        assert poly == poly
        assert not poly != poly

    def test_eq_not_polygon(self):
        verts = [(1, -2), (0, 0), (1, 0), (3, 0), (4, -2)]
        assert self.Polygon(verts) != self.Seq2(verts)
        assert not self.Polygon(verts) == self.Seq2(verts)
        assert self.Polygon(verts) != None
        assert not self.Polygon(verts) == None

    def test_eq_different_lengths(self):
        poly1 = self.Polygon([(0,0), (1,0), (1,1), (-1, 1), (0,0)])
        poly2 = self.Polygon([(0,0), (1,0), (1,1), (-1, 1)])
        assert not poly1 == poly2
        assert poly1 != poly2

    def test_eq_different_verts(self):
        poly1 = self.Polygon([(0,0), (1,0), (1,1), (-1, 1)])
        poly2 = self.Polygon([(0,0), (1,0), (1,1), (0, 1)])
        assert not poly1 == poly2
        assert poly1 != poly2
    
    def test_eq_different_starting_vert(self):
        poly1 = self.Polygon([(-3,3), (-1,-2), (1,-2), (3,3), (1,-1), (-1,-1)])
        poly2 = self.Polygon([(3,3), (1,-1), (-1,-1), (-3,3), (-1,-2), (1,-2)])
        assert poly1 == poly2
        assert not poly1 != poly2
        poly3 = self.Polygon([(3,3), (1,0), (-1,-1), (-4,3), (-1,-2), (1,-2)])
        assert poly1 != poly3
        assert not poly1 == poly3

    def test_eq_different_winding(self):
        verts = [(1, -2), (0, 0), (1, 0), (3, 0), (4, -2)]
        poly1 = self.Polygon(verts)
        verts.reverse()
        poly2 = self.Polygon(verts)
        assert poly1 == poly2
        assert not poly1 != poly2
        poly3 = self.Polygon(verts[2:] + verts[:2])
        assert poly1 == poly3
        assert not poly1 != poly3
        verts[2] = (0.5, 0)
        poly4 = self.Polygon(verts)
        assert not poly1 == poly4
        assert poly1 != poly4

    def test_eq_degenerate_cases(self):
        verts = [(0,0)]*3 + [(0,1)] + [(0,0)]*2
        assert self.Polygon(verts) == self.Polygon(verts)
        assert self.Polygon(reversed(verts)) == self.Polygon(verts)
        assert self.Polygon(verts) == self.Polygon(verts[:-2] + verts[-2:])
        # Rect with coincident edges
        verts = [(0,0), (0,1), (1,1), (1,0), (0,0), (0,1), (1,1), (1,0)]
        assert self.Polygon(verts) == self.Polygon(verts)
        assert self.Polygon(reversed(verts)) == self.Polygon(verts)
        assert self.Polygon(verts) == self.Polygon(verts[:1] + verts[1:])
        # Different repeating verts
        poly1 = self.Polygon([(0,0), (0,1), (0,1), (0,1), (1,1)])
        poly2 = self.Polygon([(0,0), (0,1), (1,1), (1,1), (1,1)])
        assert poly1 != poly2
        poly3 = self.Polygon([(1,1), (0,1), (0,1), (0,1), (0,0)])
        assert poly1 == poly3
        assert not poly2 == poly3

    def test_contains_point_triangle(self):
        poly = self.Polygon([(0,1), (1, -1), (-0.5,-0.5)])
        assert poly.contains_point((0, 0))
        assert poly.contains_point((-0.2, -0.2))
        assert poly.contains_point(self.Vec2(0, 0.9))
        assert poly.contains_point((0.5, -0.5))
        assert not poly.contains_point(self.Vec2(-0.7, 0.9))
        assert not poly.contains_point(self.Vec2(-0.4, 0))
        assert not poly.contains_point(self.Vec2(0.4, 0.5))
        assert not poly.contains_point((100, 0))
        assert not poly.contains_point((-100, 0))
        assert not poly.contains_point((0, -100))
        assert not poly.contains_point((0, 100))
        assert not poly.contains_point((-100, -100))
        assert not poly.contains_point((100, -100))
        assert not poly.contains_point((-100, 100))
        assert not poly.contains_point((100, 100))

    def test_contains_point_triangle_with_mutation(self):
        poly = self.Polygon([(0,0), (1, -1), (0.5,0.5)])
        assert poly.contains_point((0.5, -0.1))
        poly[1] = (1, 0)
        assert not poly.contains_point((0.5, -0.1))

    def test_contains_point_degenerate_triangle(self):
        poly = self.Polygon([(2,3), (2,0), (2,5)])
        assert not poly.contains_point((0,0))
        assert not poly.contains_point((2,0))
        assert not poly.contains_point((2,4))
        assert not poly.contains_point((0,4))
        assert not poly.contains_point((2.1,4))

    def test_contains_point_null_triangle(self):
        poly = self.Polygon([(1,1), (1,1), (1,1)])
        assert not poly.contains_point((0,0))
        assert not poly.contains_point((1,1))
        assert not poly.contains_point((2,2))

    def test_contains_point_convex_no_centroid(self):
        poly = self.Polygon(
            [(1,1), (0,2), (-0.9, 1.5), (-1,0.5), (-1,-1), (0.5,-1)])
        assert poly.is_convex
        assert not poly.is_centroid_known
        assert poly.contains_point((0, 0))
        assert poly.contains_point((0, 1))
        assert poly.contains_point((0.5, 1))
        assert poly.contains_point((-0.5, -0.5))
        assert poly.contains_point(self.Vec2(-0.75, 0.5))
        assert not poly.contains_point((-1.1, 0.5))
        assert not poly.contains_point((1, 0))
        assert not poly.contains_point((-1.01, -1))
        assert not poly.contains_point(self.Vec2(-0.5, -10))
        assert not poly.contains_point((100, 0))
        assert not poly.contains_point((-100, 0))
        assert not poly.contains_point((0, -100))
        assert not poly.contains_point((0, 100))
        assert not poly.contains_point((-100, -100))
        assert not poly.contains_point((100, -100))
        assert not poly.contains_point((-100, 100))
        assert not poly.contains_point((100, 100))

    def test_contains_point_convex_with_mutation(self):
        poly = self.Polygon(
            [(-1.5,0), (0,2), (1, 0), (1.5,-2), (-0.5,-2), (-1,-1.5)])
        assert poly.is_convex
        assert poly.contains_point((0, 0))
        assert poly.contains_point((1,-1.5))
        poly[3] = (0.5,-2)
        assert poly.is_convex
        assert poly.contains_point((0, 0))
        assert not poly.contains_point((1,-1.5))

    def test_contains_point_regular(self):
        poly = self.Polygon.regular(8, 1.5, center=(1,1), angle=22.5)
        assert poly.is_centroid_known
        assert poly.contains_point((1, 1))
        assert poly.contains_point((-0.25, 1))
        assert poly.contains_point((0, 1))
        assert poly.contains_point((1, -0.2))
        assert poly.contains_point((0.75, -0.38))
        assert poly.contains_point(self.Vec2(-0.3, 1.2))
        assert not poly.contains_point((0, 0))
        assert not poly.contains_point((2, 2))
        assert not poly.contains_point(self.Vec2(-0.5, -0.5))
        assert not poly.contains_point((2.6, 1))
        assert not poly.contains_point((0, 2.6))
        assert not poly.contains_point((100, 0))
        assert not poly.contains_point((-100, 0))
        assert not poly.contains_point((0, -100))
        assert not poly.contains_point((0, 100))
        assert not poly.contains_point((-100, -100))
        assert not poly.contains_point((100, -100))
        assert not poly.contains_point((-100, 100))
        assert not poly.contains_point((100, 100))

    def test_contains_point_radial_concave(self):
        poly = self.Polygon.star(4, 4, 1)
        assert poly.is_centroid_known
        assert poly.contains_point((0, 0))
        assert poly.contains_point((0, 3))
        assert poly.contains_point(poly[3])
        assert poly.contains_point((-3, 0))
        assert poly.contains_point((-4, 0))
        assert poly.contains_point(poly[5])
        assert poly.contains_point((3.99, 0))
        assert poly.contains_point((0, 3.99))
        assert not poly.contains_point((4, 0))
        assert not poly.contains_point((0, 4))
        assert not poly.contains_point(poly[1])
        assert not poly.contains_point(poly[7])
        assert not poly.contains_point((-1.1, 1.1))
        assert not poly.contains_point((-1, 2))
        assert not poly.contains_point((1, 2))
        assert not poly.contains_point((-2, 1))
        assert not poly.contains_point((-2, -1))
        assert not poly.contains_point((-1, -2))
        assert not poly.contains_point((1, -2))
        assert not poly.contains_point((2, 1))
        assert not poly.contains_point((2, -1))
        assert not poly.contains_point((100, 0))
        assert not poly.contains_point((-100, 0))
        assert not poly.contains_point((0, -100))
        assert not poly.contains_point((0, 100))
        assert not poly.contains_point((-100, -100))
        assert not poly.contains_point((100, -100))
        assert not poly.contains_point((-100, 100))
        assert not poly.contains_point((100, 100))

    def test_contains_point_concave(self):
        poly = self.Polygon([(-1,0), (-1,1), (2,1), (2,0), (1.5,-1), 
            (1,0), (0.5,-1), (0,0), (-0.5,-1)])
        assert not poly.is_convex
        assert poly.is_simple
        assert poly.contains_point((1, 0.5))
        assert poly.contains_point((-0.5, -0.25))
        assert poly.contains_point((0.5, -0.6))
        assert poly.contains_point((1.5, -0.1))
        assert poly.contains_point((-0.5, -0.999))
        assert poly.contains_point((0.5, 0))
        assert not poly.contains_point((0, 1.1))
        assert not poly.contains_point((0.5, -1.1))
        assert not poly.contains_point((0.9, 2.1))
        assert not poly.contains_point((-0.9, -0.5))
        assert not poly.contains_point((0, -0.1))
        assert not poly.contains_point((0.4, -0.9))
        assert not poly.contains_point((1, -0.1))
        assert not poly.contains_point((1.8, -0.8))
        assert not poly.contains_point((100, 0))
        assert not poly.contains_point((-100, 0))
        assert not poly.contains_point((0, -100))
        assert not poly.contains_point((0, 100))
        assert not poly.contains_point((-100, -100))
        assert not poly.contains_point((100, -100))
        assert not poly.contains_point((-100, 100))
        assert not poly.contains_point((100, 100))

    def test_contains_point_non_simple(self):
        poly = self.Polygon([(2,-2), (-2,-2), (-2,2), (0,2), (0,-1), 
            (1,-1), (1,0), (-1,0), (-1,1), (2,1)])
        assert not poly.is_convex
        assert not poly.is_simple
        assert poly.contains_point((0.5, 0.5))
        assert poly.contains_point((1.5, 0.5))
        assert poly.contains_point((1.5, -1.5))
        assert poly.contains_point((-1, -1))
        assert poly.contains_point((-1.5, 0.5))
        assert poly.contains_point((-0.5, 1.5))
        assert poly.contains_point((-0.5, 0.5)) # self-overlap
        assert not poly.contains_point((1, 1.5))
        assert not poly.contains_point((1.5, 1.5))
        assert not poly.contains_point((2.1, 0))
        assert not poly.contains_point((-2.1, 0))
        assert not poly.contains_point((0, -2.1))
        assert not poly.contains_point((0, 2.1))
        assert not poly.contains_point((0.5, 2.1))
        assert not poly.contains_point((0.5, -0.5)) # hole
        assert not poly.contains_point((100, 0))
        assert not poly.contains_point((-100, 0))
        assert not poly.contains_point((0, -100))
        assert not poly.contains_point((0, 100))
        assert not poly.contains_point((-100, -100))
        assert not poly.contains_point((100, -100))
        assert not poly.contains_point((-100, 100))
        assert not poly.contains_point((100, 100))

    def test_contains_point_degenerate(self):
        poly = self.Polygon([(-2,1), (2,1), (3,1), (5,1), (5.2,1)])
        assert not poly.contains_point((0,0))
        assert not poly.contains_point((2,1))
        assert not poly.contains_point((5,1))
        assert not poly.contains_point((5.2,1))
        assert not poly.contains_point((-2.1,1))
        assert not poly.contains_point((2.1,4))

    def test_contains_point_exclusive_triangles(self):
        tris = [
            self.Polygon([(0,0), (0,3), (3,3)]),
            self.Polygon([(0,0), (3,0), (3,3)]),
            self.Polygon([(-1,-1), (0,0), (0,3)]),
            self.Polygon([(3,3), (0,3), (1,4)]),
        ]
        assert_contains_point(tris, 0, (0, 1))
        assert_contains_point(tris, 0, (0, 2))
        assert_contains_point(tris, 0, (0, 3))
        assert_contains_point(tris, 0, (1.5, 3))
        assert_contains_point(tris, 1, (2, 2))
        assert_contains_point(tris, 1, (1, 1))
        assert_contains_point(tris, None, (0, 0))
        assert_contains_point(tris, None, (1.5, 0))
        assert_contains_point(tris, None, (3, 0))
        assert_contains_point(tris, None, (3, 1.5))
        assert_contains_point(tris, None, (3, 3))

    def test_contains_point_exclusive_convex(self):
        polys = [
            self.Polygon([(2,2), (0,0), (-2,1), (0,3)]),
            self.Polygon([(0,-1), (0,0), (-2,1), (-2,-3)]),
            self.Polygon([(2,-1), (0,-1), (0,0), (2,2)]),
        ]
        assert polys[0].is_convex
        assert polys[1].is_convex
        assert polys[2].is_convex
        assert_contains_point(polys, 0, (-1, 2))
        assert_contains_point(polys, 0, (-2, 1))
        assert_contains_point(polys, 0, (-1, 0.5))
        assert_contains_point(polys, 1, (-1, 0))
        assert_contains_point(polys, 1, (-2, 0))
        assert_contains_point(polys, 1, (-2, -2))
        assert_contains_point(polys, 2, (0, 0))
        assert_contains_point(polys, 2, (1, 1))
        assert_contains_point(polys, 2, (0, -0.5))
        assert_contains_point(polys, None, (0, -1))
        assert_contains_point(polys, None, (1, -1))
        assert_contains_point(polys, None, (2, -1))
        assert_contains_point(polys, None, (2, 0))
        assert_contains_point(polys, None, (-1, -2))
        assert_contains_point(polys, None, (-2, -3))
        assert_contains_point(polys, None, (0, 3))
        assert_contains_point(polys, None, (1.5, 2.5))
        assert_contains_point(polys, None, (2, 2))

    def test_contains_point_exclusive_concave(self):
        polys = [
            self.Polygon([(0,0), (0,1), (1,1), (2,2), (3,2), (3,0)]),
            self.Polygon([(2,2), (1,1), (0,1), (1,2), (0,3), (1,3)]),
            self.Polygon([(4,3), (1,3), (2,2), (3,2), (3,0), 
                (4,0), (5,2), (5,1)]),
        ]
        assert not polys[0].is_convex
        assert not polys[1].is_convex
        assert not polys[2].is_convex
        assert_contains_point(polys, 0, (0, 1))
        assert_contains_point(polys, 0, (0, 0.5))
        assert_contains_point(polys, 0, (1, 1))
        assert_contains_point(polys, 0, (1.5, 1.5))
        assert_contains_point(polys, 0, (2, 2))
        assert_contains_point(polys, 0, (2.5, 2))
        assert_contains_point(polys, 1, (0, 3))
        assert_contains_point(polys, 1, (0.5, 3))
        assert_contains_point(polys, 1, (0.5, 2.5))
        assert_contains_point(polys, 1, (1, 2))
        assert_contains_point(polys, 1, (0.5, 1.5))
        assert_contains_point(polys, 2, (3, 2))
        assert_contains_point(polys, 2, (3, 1))
        assert_contains_point(polys, 2, (1, 3))
        assert_contains_point(polys, 2, (2, 3))
        assert_contains_point(polys, 2, (1.5, 2.5))
        assert_contains_point(polys, None, (0, 0))
        assert_contains_point(polys, None, (1, 0))
        assert_contains_point(polys, None, (3, 0))
        assert_contains_point(polys, None, (3.5, 0))
        assert_contains_point(polys, None, (4, 0))
        assert_contains_point(polys, None, (4, 3))
        assert_contains_point(polys, None, (4.5, 2))
        assert_contains_point(polys, None, (4.5, 1))
        assert_contains_point(polys, None, (5, 2))
        assert_contains_point(polys, None, (5, 1.5))
        assert_contains_point(polys, None, (5, 1))

    def test_tangents_to_point_convex(self):
        poly = self.Polygon.regular(30, 2)
        assert_equal(poly.tangents_to_point((0,10)), 
            (self.Vec2.polar(12, 2), self.Vec2.polar(168, 2)))
        assert_equal(poly.tangents_to_point((0,5)), 
            (self.Vec2.polar(24, 2), self.Vec2.polar(156, 2)))
        assert_equal(poly.tangents_to_point((10,10)), 
            (self.Vec2.polar(-36, 2), self.Vec2.polar(132, 2)))
        assert_equal(poly.tangents_to_point((2,2)), 
            (self.Vec2.polar(0, 2), self.Vec2.polar(96, 2)))
        assert_equal(poly.tangents_to_point((-2,-2)), 
            (self.Vec2.polar(180, 2), self.Vec2.polar(-84, 2)))
        assert_equal(poly.tangents_to_point((-2,-20)), 
            (self.Vec2.polar(180, 2), self.Vec2.polar(-12, 2)))
        assert_equal(poly.tangents_to_point((5,20)), 
            (self.Vec2.polar(-12, 2), self.Vec2.polar(156, 2)))

    def test_tangents_to_point_convex_reverse_wound(self):
        poly = self.Polygon(reversed(self.Polygon.regular(30, 2)))
        assert_equal(poly.tangents_to_point((0,10)), 
            (self.Vec2.polar(12, 2), self.Vec2.polar(168, 2)))
        assert_equal(poly.tangents_to_point((0,-5)), 
            (self.Vec2.polar(-156, 2), self.Vec2.polar(-24, 2)))
        assert_equal(poly.tangents_to_point((10,10)), 
            (self.Vec2.polar(-36, 2), self.Vec2.polar(132, 2)))
        assert_equal(poly.tangents_to_point((2,2)), 
            (self.Vec2.polar(0, 2), self.Vec2.polar(96, 2)))
        assert_equal(poly.tangents_to_point((-2,-2)), 
            (self.Vec2.polar(180, 2), self.Vec2.polar(-84, 2)))
        assert_equal(poly.tangents_to_point((-2,-20)), 
            (self.Vec2.polar(180, 2), self.Vec2.polar(-12, 2)))
        assert_equal(poly.tangents_to_point((5,20)), 
            (self.Vec2.polar(-12, 2), self.Vec2.polar(156, 2)))

    def test_tangents_to_interior_point_convex(self):
        # Although the results of this are undefined, we need 
        # to ensure the library is at least well-behaved
        poly = self.Polygon.regular(30, 2)
        verts = list(poly)
        assert poly.contains_point((0, 0))
        left, right = poly.tangents_to_point((0, 0))
        assert left in verts
        assert right in verts

    def test_tangents_to_point_non_convex(self):
        poly = self.Polygon([(1,-1), (0,-3), (-1,3), (0,1), (2,2), (2,-2)])
        assert not poly.is_convex
        assert_equal(poly.tangents_to_point((2.1,1)), ((2,-2), (2,2)))
        assert_equal(poly.tangents_to_point((0,-4)), ((-1,3), (2,-2)))
        assert_equal(poly.tangents_to_point((1,-4)), ((0,-3), (2,-2)))
        assert_equal(poly.tangents_to_point((20,20)), ((2,-2), (-1,3)))
        assert_equal(poly.tangents_to_point((-5,2)), ((-1,3), (0,-3)))

    def test_tangents_to_interior_point_non_convex(self):
        # Although the results of this are undefined, we need 
        # to ensure the library is at least well-behaved
        verts = [(1,-1), (0,-3), (-1,3), (0,1), (2,2), (2,-2)]
        poly = self.Polygon(verts)
        assert not poly.is_convex
        assert poly.contains_point((0, 0))
        left, right = poly.tangents_to_point((0, 0))
        assert left in verts
        assert right in verts

    def test_convex_hull_triangle(self):
        points = [(0,0), (1, -2), (2, 3)]
        hull = self.Polygon.convex_hull(points)
        assert hull.is_convex
        assert_equal(hull, self.Polygon(points))
        points = [(0,0), (1, 2), (2, 3)]
        hull = self.Polygon.convex_hull(points)
        assert hull.is_convex
        assert_equal(hull, self.Polygon(points))

    def confirm_hull(self, points, hull):
        poly = self.Polygon(list(hull))
        assert poly.is_convex, hull
        for pt in hull:
            assert pt in points, "Hull pt %r not in points" % pt
        for pt in points:
            assert poly.contains_point(pt) or pt in hull, (
                "Pt %r outside hull %r" % (pt, hull))

    def test_convex_hull_random_points(self):
        points = [(55,27), (53,95), (57,15), (55,24), (54,0), (3,28), (21,93),
            (10,86), (17,74), (51,44), (7,4), (5,93), (25,86), (20,55),
            (27,24), (47,52), (55,62), (57,85), (71,71), (75,46), (90,10),
            (25,42), (62,72), (36,38), (27,52), (69,17), (93,40), (70,51),
            (77,80), (43,88), (88,74), (91,76), (63,45), (40,13), (10,59),
            (8,16), (3,63), (18,67), (47,65), (88,65), (19,25), (14,2),
            (55,97), (41,70), (83,86), (0,80), (46,78), (12,20), (54,46),
            (48,72), (25,34), (67,68), (24,22), (91,63), (58,88), (100,77),
            (93,73), (43,65), (2,27), (81,2), (53,52), (64,3), (16,76),
            (8,10), (64,18), (93,48), (93,96), (37,17), (48,83), (96,94),
            (56,21), (36,6), (82,92), (2,88), (1,7), (99,42), (56,48), (35,0),
            (54,7), (92,57), (26,11), (31,28), (31,73), (54,7), (91,52),
            (40,31), (15,78), (67,6), (89,72), (9,3), (25,58), (6,86),
            (58,75), (17,63), (32,11), (71,71), (95,53), (22,78), (63,78),
            (88,33)]
        hull = self.Polygon.convex_hull(points)
        self.confirm_hull(points, hull)

    def test_convex_hull_convex_input_ordered(self):
        points = self.Polygon.regular(33, 5)
        hull = self.Polygon.convex_hull(points)
        assert points == hull, (list(points), list(hull))

    def test_convex_hull_almost_convex_input_unordered(self):
        points = [(-1.57211, 1.23632), (1.16011, -1.62915), 
            (1.85674, -0.743325), (-1.77767, 0.916453), (1.85674, 0.743325),
            (-1.77767, -0.916453), (1.44747, -1.38016), (0.471518, 1.94362),
            (-1.30972, 1.5115), (2, 0), (1.96386, 0.378502), 
            (-1.99094, -0.190112), (1.16011, 1.62915), (0.0951638, -1.99773), 
            (1.96386, -0.378502), (-1, -1.73205), (-0.28463, 1.97964), 
            (0.0951638, 1.99773), (-0.28463, -1.97964), (0.471518, -1.94362), 
            (-1.91899, -0.563465), (1.44747, 1.38016), (1.44747, 1.379), 
            (-0.654136, 1.89), (-1.99094, 0.190112), (-1.57211, -1.23632), 
            (-1.91899, 0.563465), (0.83083, -1.81926), (1.68251, 1.08128), 
            (-1.30972, -1.5115), (-1, 1.73205), (-0.654136, -1.89), 
            (0.83083, 1.81926), (1.68251, -1.08128),]
        hull = self.Polygon.convex_hull(points)
        assert len(hull) == len(points) - 1, (len(hull), len(points))
        self.confirm_hull(points, hull)

    def test_convex_hull_degenerate(self):
        points = [(0,1), (2,1), (5,1), (7,1), (12,1)]
        hull = list(self.Polygon.convex_hull(points))
        assert (0,1) in points
        assert (12,1) in points
        assert_equal(len(hull), 3)
        while hull:
            pt = hull.pop()
            assert pt[1] == 1, pt
            assert 0 <= pt[0] <= 12, pt

    def test_str_and_repr(self):
        poly = self.Polygon([(0.25,3.5), (1.3,4.25), (0.16,2.25), (-0.5,0.16)])
        assert_equal(repr(poly), 
            "Polygon([(0.25, 3.5), (1.3, 4.25), (0.16, 2.25), (-0.5, 0.16)])")
        assert_equal(repr(poly), str(poly))
        assert not poly.is_convex
        assert poly.is_simple
        assert_equal(repr(poly), 
            "Polygon([(0.25, 3.5), (1.3, 4.25), (0.16, 2.25), (-0.5, 0.16)], "
            "is_convex=False, is_simple=True)")
        assert_equal(repr(poly), str(poly))
        poly = self.Polygon([(1.3,1.5), (0.16,0.16), (2.25,2.25)])
        assert poly.is_convex
        assert_equal(repr(poly),
            "Polygon([(1.3, 1.5), (0.16, 0.16), (2.25, 2.25)], is_convex=True)")
        assert_equal(repr(poly), str(poly))

    def test_copy(self):
        from copy import copy
        p = self.Polygon([(0,0), (1,0), (1,1), (0,1)])
        assert p.is_convex
        centroid = p.centroid
        c = copy(p)
        assert isinstance(c, self.Polygon)
        assert c is not p
        assert_equal(tuple(c), tuple(p))
        assert c.is_convex_known
        assert c.is_convex
        assert c.is_simple_known
        assert c.is_simple
        assert c.is_centroid_known
        assert_equal(c.centroid, centroid)
        c[0] = (0,0.1)
        assert c[0] != p[0]

        p = self.Polygon([(0,0), (1,1), (1,0), (0,1)])
        assert not p.is_simple
        c = copy(p)
        assert isinstance(c, self.Polygon)
        assert c is not p
        assert_equal(tuple(c), tuple(p))
        assert c.is_convex_known
        assert not c.is_convex
        assert c.is_simple_known
        assert not c.is_simple
        c[0] = (0,0.1)
        assert c[0] != p[0]

    def test_copy_subclass(self):
        from copy import copy
        class PolySubclass(self.Polygon):
            from_points_called = False
            @classmethod
            def from_points(cls, points):
                cls.from_points_called = True
                return super(PolySubclass, cls).from_points(points)

        a = PolySubclass([(0,1), (1,2), (3,4)])
        assert not PolySubclass.from_points_called
        b = copy(a)
        assert PolySubclass.from_points_called
        assert a is not b
        assert isinstance(b, PolySubclass)
        assert_equal(tuple(a), tuple(b))
        a[0] = (0, 0)
        assert_equal(b[0], self.Vec2(0, 1))

    def test_deepcopy(self):
        from copy import deepcopy
        p = self.Polygon([(0,0), (1,0), (1,1), (0,1)])
        bbox = p.bounding_box
        c = deepcopy(p)
        assert isinstance(c, self.Polygon)
        assert c is not p
        assert_equal(tuple(c), tuple(p))
        c[0] = (0,0.1)
        assert c[0] != p[0]
        assert c.bounding_box is not bbox

    def test_imul_by_transform(self):
        b = a = self.Polygon([(1,2), (3,4), (5,6)])
        a *= self.Affine.translation((5, -4))
        assert a is b
        V = self.Vec2
        assert_equal(tuple(a), (V(6, -2), V(8, 0), V(10, 2)))

    @raises(TypeError)
    def test_imul_incompatible(self):
        a = self.Polygon([(1,2), (3,4), (5,6)])
        a *= None

    def test_mul_by_transform(self):
        a = self.Polygon([(1,2), (3,4), (5,6)])
        b = a * self.Affine.scale((2, -1))
        assert a is not b
        assert isinstance(b, self.Polygon)
        V = self.Vec2
        assert_equal(tuple(b), (V(2, -2), V(6, -4), V(10, -6)))

    @raises(TypeError)
    def test_mul_incompatible(self):
        a = self.Polygon([(1,2), (3,4), (5,6)]) * 2


class PyPolygonTestCase(PolygonBaseTestCase, unittest.TestCase):
    from planar.vector import Vec2, Seq2
    from planar.transform import Affine
    from planar.box import BoundingBox
    from planar.polygon import Polygon


class CPolygonTestCase(PolygonBaseTestCase, unittest.TestCase):
    from planar.c import Vec2, Seq2, Affine, BoundingBox
    from planar.c import Polygon


class PyPolygonWhiteBoxTestCase(unittest.TestCase):
    from planar.vector import Vec2, Seq2
    from planar.polygon import Polygon

    def test_split_y_polylines_convex(self):
        poly = self.Polygon([(-1,0), (-1,1), (-0.5,2), (0,2), 
            (0.5,1.5), (0.5,-1), (-0.8, -0.5)])
        assert poly._y_polylines is None
        assert poly.is_convex
        assert_equal(poly._y_polylines, (
            [(-1,0.5), (-0.5,-0.8), (0,-1), (1,-1), (2,-0.5)],
            [(-1,0.5), (1.5,0.5), (2,0), (2,-0.5)]))

    def test_split_y_polylines_straight_edge(self):
        poly = self.Polygon([(0,0), (0,3), (1,2), (1,1)], is_convex=True)
        assert_equal(poly._y_polylines, (
            [(0,0), (3,0)],
            [(0,0), (1,1), (2,1), (3,0)]))
        poly = self.Polygon([(2,0), (2,3), (1,2), (1,1)], is_convex=True)
        assert_equal(poly._y_polylines, (
            [(0,2), (1,1), (2,1), (3,2)],
            [(0,2), (3,2)]))


if __name__ == '__main__':
    unittest.main()


# vim: ai ts=4 sts=4 et sw=4 tw=78

