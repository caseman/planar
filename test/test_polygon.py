"""Polygon class unit tests"""

from __future__ import division
import sys
import math
import unittest
from nose.tools import assert_equal, assert_almost_equal, raises


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


class PyPolygonTestCase(PolygonBaseTestCase, unittest.TestCase):
    from planar.vector import Vec2, Seq2
    from planar.box import BoundingBox
    from planar.polygon import Polygon


if __name__ == '__main__':
    unittest.main()


# vim: ai ts=4 sts=4 et sw=4 tw=78

