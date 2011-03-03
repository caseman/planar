"""Line unit tests"""

from __future__ import division
import sys
import math
import unittest
from nose.tools import assert_equal, assert_almost_equal, raises


class LineBaseTestCase(object):

    @raises(TypeError)
    def test_no_args(self):
        self.Line()

    @raises(TypeError)
    def test_too_few_args(self):
        self.Line((0,0))

    @raises(TypeError)
    def test_wrong_arg_types(self):
        self.Line("foo", 2)

    @raises(TypeError)
    def test_too_many_args(self):
        self.Line((0,0), (1,1), (2,2))

    def test_direction_and_offset(self):
        line = self.Line((1,1), (1, -1))
        assert_equal(line.direction, self.Vec2(1,-1).normalized())
        assert_almost_equal(line.offset, -self.Vec2(1,1).length)
        line = self.Line((1,1), (-1, 1))
        assert_equal(line.direction, self.Vec2(-1,1).normalized())
        assert_almost_equal(line.offset, self.Vec2(1,1).length)
    
    def test_direction_and_offset_thru_origin(self):
        line = self.Line((0,0), (-1,4))
        assert_equal(line.offset, 0)
        assert_equal(line.direction, self.Vec2(-1,4).normalized())

    @raises(TypeError)
    def test_from_points_too_few_args(self):
        self.Line.from_points()

    @raises(TypeError)
    def test_from_points_not_iterable(self):
        self.Line.from_points(100)

    @raises(ValueError)
    def test_from_points_wrong_iterable(self):
        self.Line.from_points("foo")

    @raises(ValueError)
    def test_from_points_too_few(self):
        self.Line.from_points([(1,1)])

    @raises(ValueError)
    def test_from_points_too_few_distinct(self):
        self.Line.from_points([(0,1), (0,1), (0,1)])

    def test_from_points_two(self):
        line = self.Line.from_points([(1,0), (3,1)])
        assert_equal(line.direction, self.Vec2(2,1).normalized())
        assert_equal(line.normal, self.Vec2(1,-2).normalized())
        assert_almost_equal(line.offset, line.project((0,0)).length)

    def test_from_points_many_collinear(self):
        line = self.Line.from_points(
            [(-3,-9), (-7,-21), (1, 3), (1003,3009), (5,15)])
        assert_equal(line.direction, self.Vec2(-1,-3).normalized())
        assert_equal(line.normal, self.Vec2(-3,1).normalized())
        assert_almost_equal(line.offset, 0)

    def test_from_points_iter(self):
        line = self.Line.from_points(iter([(-10,5), (-10,5), (-5,4), (0,3)]))
        assert_equal(line.direction, self.Vec2(5,-1).normalized())
        assert_equal(line.normal, self.Vec2(-1,-5).normalized())

    @raises(ValueError)
    def test_from_points_many_not_collinear(self):
        self.Line.from_points([(0,0.5), (3,1.5), (9,4.5), (10,4.5)])

    @raises(TypeError)
    def test_from_normal_no_args(self):
        self.Line.from_normal()

    @raises(TypeError)
    def test_from_normal_wrong_arg_types(self):
        self.Line.from_normal(0, "baz")

    def test_from_normal(self):
        line = self.Line.from_normal((0.25,0.5), 3)
        assert_equal(line.direction, self.Vec2(-2,1).normalized())
        assert_equal(line.normal, self.Vec2(1,2).normalized())
        assert_equal(line.offset, 3)

    def test_set_direction(self):
        line = self.Line((2,0), (0,1))
        assert_equal(line.offset, 2)
        line.direction = (-1, -5)
        assert_equal(line.direction, self.Vec2(-1,-5).normalized())
        assert_equal(line.normal, self.Vec2(-5,1).normalized())
        assert_equal(line.offset, 2)
        line.direction = self.Vec2(-3, -2)
        assert_equal(line.direction, self.Vec2(-3,-2).normalized())
        assert_equal(line.normal, self.Vec2(-2,3).normalized())
        assert_equal(line.offset, 2)

    def test_set_normal(self):
        line = self.Line((0,4), (2,0))
        assert_equal(line.offset, -4)
        line.normal = (-1, -2)
        assert_equal(line.direction, self.Vec2(2,-1).normalized())
        assert_equal(line.normal, self.Vec2(-1,-2).normalized())
        assert_equal(line.offset, -4)
        line.normal = self.Vec2(2, -2)
        assert_equal(line.direction, self.Vec2(2,2).normalized())
        assert_equal(line.normal, self.Vec2(2,-2).normalized())
        assert_equal(line.offset, -4)

    def test_distance_to_horizontal(self):
        line = self.Line((0,2), (1,0))
        assert_equal(line.distance_to((0, 2)), 0)
        assert_equal(line.distance_to((7, 2)), 0)
        assert_equal(line.distance_to((-7, 2)), 0)
        assert_equal(line.distance_to((-100, 2)), 0)
        assert_equal(line.distance_to((1, 2.5)), -0.5)
        assert_equal(line.distance_to((-3, 2.5)), -0.5)
        assert_equal(line.distance_to((-3, 5)), -3)
        assert_equal(line.distance_to((-1, -0.5)), 2.5)
        assert_equal(line.distance_to((-3, -0.5)), 2.5)
        assert_equal(line.distance_to((3, -5)), 7)

    def test_distance_to(self):
        line = self.Line((-1, 1), (1, 1))
        assert_almost_equal(line.distance_to((0,0)), math.sqrt(2))
        assert_almost_equal(line.distance_to(self.Vec2(-2,2)), -math.sqrt(2))
        assert_almost_equal(line.distance_to((4,2)), 2 * math.sqrt(2))
        line = self.Line((-1, 1), (-1, -1))
        assert_almost_equal(line.distance_to((0,0)), -math.sqrt(2))
        assert_almost_equal(line.distance_to(self.Vec2(-2,2)), math.sqrt(2))
        assert_almost_equal(line.distance_to((4,2)), -2 * math.sqrt(2))

    def test_point_right(self):
        import planar
        line = self.Line((-1,2), (-1,3))
        assert line.point_right((0, 0))
        assert line.point_right(self.Vec2(-0.9, 2))
        assert line.point_right((100000, 2000))
        assert not line.point_right((-1.1, 2))
        assert not line.point_right((-1,2))
        assert not line.point_right((-1 + planar.EPSILON / 2,2))
        assert not line.point_right((-4,8))
        assert not line.point_right((-100000, -2000))

    def test_point_left(self):
        import planar
        line = self.Line((-3,-1), (40,1))
        assert line.point_left((0, 0))
        assert line.point_left(self.Vec2(-3.1, -1))
        assert line.point_left((10000, 4000))
        assert not line.point_left((0, -1))
        assert not line.point_left((-3, -1))
        assert not line.point_left((-3 + planar.EPSILON / 2, -1))
        assert not line.point_left((37, 0))
        assert not line.point_left((-10000, -4000))

    def test_point_collinear(self):
        import planar
        line = self.Line((5, -2), (13, 7))
        assert line.point_collinear((5, -2))
        assert line.point_collinear((5, -2 + planar.EPSILON / 2))
        assert line.point_collinear((5, -2 - planar.EPSILON / 2))
        assert line.point_collinear((13 * 2000 + 5, 7 * 2000 - 2))
        assert line.point_collinear(self.Vec2(5, -2))
        assert not line.point_collinear((5, -2.01))
        assert not line.point_collinear((5, -1.99))
        assert not line.point_collinear(self.Vec2(0, 0))
        assert not line.point_collinear((-100000, 50000))

    def test_parallel(self):
        line = self.Line((1,2), (3,-4))
        parallel = line.parallel((-20,3))
        assert isinstance(parallel, self.Line)
        assert parallel is not line
        assert_equal(line.direction, parallel.direction)
        assert_equal(line.normal, parallel.normal)
        assert line.offset != parallel.offset
        assert parallel.point_collinear((-20,3))

    def test_perpendicular(self):
        line = self.Line((1,2), (3,-4))
        perp = line.perpendicular((-3,7))
        assert isinstance(perp, self.Line)
        assert perp is not line
        assert_equal(perp.direction, line.direction.perpendicular())
        assert_equal(perp.normal, line.normal.perpendicular())
        assert line.offset != perp.offset
        assert perp.point_collinear((-3,7))

    def test_project_point(self):
        line = self.Line((2, 0), (1,1))
        assert line.project((0,0)).almost_equals((1, -1))
        assert line.project((-76.3,76.3)).almost_equals((1, -1))
        assert line.project(self.Vec2(3, -1)).almost_equals((2, 0))
        assert line.project((-1,-3)).almost_equals((-1, -3))

    def test_reflect_point(self):
        line = self.Line((2, 0), (1,1))
        assert line.reflect((0,0)).almost_equals((2, -2))
        assert line.reflect((-76.3,76.3)).almost_equals((78.3, -78.3))
        assert line.reflect(self.Vec2(3, -1)).almost_equals((1, 1))
        assert line.reflect((-1,-3)).almost_equals((-1, -3))

    def test_str(self):
        line = self.Line((0.55, 0), (0, 1))
        assert_equal(str(line), "Line((0.55, 0.0), (0.0, 1.0))")
        
    def test_repr(self):
        line = self.Line((0.55, 0), (0, 1))
        assert_equal(repr(line), "Line((0.55, 0.0), (0.0, 1.0))")


class PyLineTestCase(LineBaseTestCase, unittest.TestCase):
    from planar.vector import Vec2
    from planar.line import Line

if __name__ == '__main__':
    unittest.main()


# vim: ai ts=4 sts=4 et sw=4 tw=78

