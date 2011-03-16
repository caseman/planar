"""Line unit tests"""

from __future__ import division
import sys
import math
import unittest
from nose.tools import assert_equal, assert_almost_equal, raises

class LinearBaseTestCase(object):
    
    @raises(TypeError)
    def test_no_args(self):
        self.LinearType()

    @raises(TypeError)
    def test_too_few_args(self):
        self.LinearType((0,0))

    @raises(TypeError)
    def test_wrong_arg_types(self):
        self.LinearType("foo", 2)

    @raises(TypeError)
    def test_too_many_args(self):
        self.LinearType((0,0), (1,1), (2,2))

    @raises(ValueError)
    def test_null_direction(self):
        self.LinearType((1,0), (0,0))

    @raises(TypeError)
    def test_from_points_too_few_args(self):
        self.LinearType.from_points()

    @raises(TypeError)
    def test_from_points_not_iterable(self):
        self.LinearType.from_points(100)

    @raises(TypeError)
    def test_from_points_wrong_iterable(self):
        self.LinearType.from_points("foo")

    @raises(ValueError)
    def test_from_points_too_few(self):
        self.LinearType.from_points([(1,1)])

    @raises(ValueError)
    def test_from_points_too_few_distinct(self):
        self.LinearType.from_points([(0,1), (0,1), (0,1)])

    def test_from_points_two(self):
        lg = self.LinearType.from_points([(1,0), (3,1)])
        assert_equal(lg.direction, self.Vec2(2,1).normalized())
        assert_equal(lg.normal, self.Vec2(1,-2).normalized())
        if hasattr(lg, 'offset'):
            assert_almost_equal(lg.offset, lg.project((0,0)).length)

    def test_from_points_iter(self):
        lg = self.LinearType.from_points(iter([(-10,5), (-10,5), (-5,4), (0,3)]))
        assert_equal(lg.direction, self.Vec2(5,-1).normalized())
        assert_equal(lg.normal, self.Vec2(-1,-5).normalized())

    @raises(ValueError)
    def test_from_points_many_not_collinear(self):
        self.LinearType.from_points([(0,0.5), (3,1.5), (9,4.5), (10,4.5)])

    def test_set_direction(self):
        import planar
        lg = self.LinearType((2,0), (0,1))
        assert isinstance(lg.direction, planar.Vec2)
        if hasattr(lg, 'offset'):
            assert_equal(lg.offset, 2)
        lg.direction = (-1, -5)
        assert isinstance(lg.direction, planar.Vec2)
        assert_equal(lg.direction, self.Vec2(-1,-5).normalized())
        assert_equal(lg.normal, self.Vec2(-5,1).normalized())
        if hasattr(lg, 'offset'):
            assert_equal(lg.offset, 2)
        lg.direction = self.Vec2(-3, -2)
        assert isinstance(lg.direction, planar.Vec2)
        assert_equal(lg.direction, self.Vec2(-3,-2).normalized())
        assert_equal(lg.normal, self.Vec2(-2,3).normalized())
        if hasattr(lg, 'offset'):
            assert_equal(lg.offset, 2)

    @raises(TypeError)
    def test_set_direction_wrong_type(self):
        lg = self.LinearType((1, 2), (2, 3))
        lg.direction = 'yo'

    @raises(ValueError)
    def test_set_direction_null(self):
        lg = self.LinearType((1, 2), (2, 3))
        lg.direction = (0, 0)

    def test_set_normal(self):
        import planar
        lg = self.LinearType((0,4), (2,0))
        assert isinstance(lg.direction, planar.Vec2)
        if hasattr(lg, 'offset'):
            assert_equal(lg.offset, -4)
        lg.normal = (-1, -2)
        assert isinstance(lg.direction, planar.Vec2)
        assert_equal(lg.direction, self.Vec2(2,-1).normalized())
        assert_equal(lg.normal, self.Vec2(-1,-2).normalized())
        if hasattr(lg, 'offset'):
            assert_equal(lg.offset, -4)
        lg.normal = self.Vec2(2, -2)
        assert isinstance(lg.direction, planar.Vec2)
        assert_equal(lg.direction, self.Vec2(2,2).normalized())
        assert_equal(lg.normal, self.Vec2(2,-2).normalized())
        if hasattr(lg, 'offset'):
            assert_equal(lg.offset, -4)

    @raises(TypeError)
    def test_set_normal_wrong_type(self):
        lg = self.LinearType((1, 2), (2, 3))
        lg.normal = 'yo'

    @raises(ValueError)
    def test_set_normal_null(self):
        lg = self.LinearType((1, 2), (2, 3))
        lg.normal = (0, 0)


class LineBaseTestCase(LinearBaseTestCase):

    @raises(TypeError)
    def test_from_normal_no_args(self):
        self.Line.from_normal()

    @raises(TypeError)
    def test_from_normal_wrong_arg_types(self):
        self.Line.from_normal(0, "baz")

    @raises(ValueError)
    def test_from_normal_null(self):
        self.Line.from_normal((0,0), 1)

    def test_from_normal(self):
        line = self.Line.from_normal((0.25,0.5), 3)
        assert_equal(line.direction, self.Vec2(-2,1).normalized())
        assert_equal(line.normal, self.Vec2(1,2).normalized())
        if hasattr(line, 'offset'):
            assert_equal(line.offset, 3)

    def test_from_points_many_collinear(self):
        line = self.Line.from_points(
            [(-3,-9), (-7,-21), (1, 3), (1003,3009), (5,15)])
        assert_equal(line.direction, self.Vec2(-1,-3).normalized())
        assert_equal(line.normal, self.Vec2(-3,1).normalized())
        assert_almost_equal(line.offset, 0)

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

    def test_contains_point(self):
        import planar
        line = self.Line((5, -2), (13, 7))
        assert line.contains_point((5, -2))
        assert line.contains_point((5, -2 + planar.EPSILON / 2))
        assert line.contains_point((5, -2 - planar.EPSILON / 2))
        assert line.contains_point((13 * 2000 + 5, 7 * 2000 - 2))
        assert line.contains_point(self.Vec2(5, -2))
        assert line.contains_point((-8, -9))
        assert not line.contains_point((5, -2.01))
        assert not line.contains_point((5, -1.99))
        assert not line.contains_point(self.Vec2(0, 0))
        assert not line.contains_point((-100000, 50000))

    def test_points(self):
        line = self.Line((1, -5), (-1, 6))
        points = line.points
        assert_equal(len(points), 2)
        assert points[0] != points[1]
        assert line.contains_point(points[0])
        assert line.contains_point(points[1])

    def test_parallel(self):
        line = self.Line((1,2), (3,-4))
        parallel = line.parallel((-20,3))
        assert isinstance(parallel, self.Line)
        assert parallel is not line
        assert_equal(line.direction, parallel.direction)
        assert_equal(line.normal, parallel.normal)
        assert line.offset != parallel.offset
        assert parallel.contains_point((-20,3))

    def test_perpendicular(self):
        line = self.Line((1,2), (3,-4))
        perp = line.perpendicular((-3,7))
        assert isinstance(perp, self.Line)
        assert perp is not line
        assert_equal(perp.direction, line.direction.perpendicular())
        assert_equal(perp.normal, line.normal.perpendicular())
        assert line.offset != perp.offset
        assert perp.contains_point((-3,7))

    def test_project_point(self):
        line = self.Line((2, 0), (1,1))
        assert line.project((0,0)).almost_equals((1, -1))
        assert line.project((-76.3,76.3)).almost_equals((1, -1))
        assert line.project(self.Vec2(3, -1)).almost_equals((2, 0))
        assert line.project((-1,-3)).almost_equals((-1, -3))

    def test_reflect_point(self):
        line = self.Line((2, 0), (1,1))
        assert line.reflect((0,0)).almost_equals((2, -2)), line.reflect((0,0))
        assert line.reflect((-76.3,76.3)).almost_equals((78.3, -78.3))
        assert line.reflect(self.Vec2(3, -1)).almost_equals((1, 1))
        assert line.reflect((-1,-3)).almost_equals((-1, -3))

    def test_equals(self):
        line = self.Line((1,-2), (2, 5))
        assert line == line
        assert line == self.Line((1,-2), (2, 5))
        assert line == self.Line.from_normal(line.normal, line.offset)
        assert not line == self.Line((1, -2), (2, 4))
        assert not line == self.Line.from_normal((2,2), line.offset)
        assert not line == None
        assert not line == ((1,-2), (2, 5))

    def test_not_equals(self):
        line = self.Line((1,-2), (2, 5))
        assert not line != line
        assert not line != self.Line((1,-2), (2, 5))
        assert line != self.Line((3,-2), (2, 5))
        assert line != self.Line((1,-2), (0, 5))
        assert line != None
        assert line != ((1,-2), (2, 5))

    def test_almost_equals(self):
        line = self.Line((1,-2), (2, 5))
        assert line.almost_equals(self.Line.from_points([(-1,-7), (5,8)]))
        assert line.almost_equals(line)
        assert not line.almost_equals(self.Line((1,-1.99), (2, 5)))
        assert not line.almost_equals(None)

    def test_transform(self):
        line = self.Line((0, 0), (-2, 1))
        line2 = line * self.Affine.rotation(-90, pivot=(-4, 2))
        assert isinstance(line2, self.Line)
        assert line2 is not line
        assert line2.direction.almost_equals(
            self.Vec2(1, 2).normalized())
        assert line2.contains_point((-4, 2))

    def test_imul_transform(self):
        line = orig = self.Line((0, 0), (1, 1))
        line *= self.Affine.translation((-1,1)) * self.Affine.scale((1, 0.5))
        assert line is orig
        assert line.direction.almost_equals(
            self.Vec2(1, 0.5).normalized()), (line.direction, self.Vec2(1, 0.5).normalized())
        assert line.contains_point((-1, 1))

    @raises(TypeError)
    def test_imul_incompatible(self):
        line = self.Line((0, 0), (1, 1))
        line *= 2


class RayBaseTestCase(LinearBaseTestCase):
    
    def test_from_points_many_collinear(self):
        ray = self.Ray.from_points(
            [(-7,-21), (-3,-9), (1, 3), (1003,3009), (5,15)])
        assert_equal(ray.direction, self.Vec2(1,3).normalized())
        assert_equal(ray.normal, self.Vec2(3,-1).normalized())

    def test_set_anchor(self):
        import planar
        ray = self.Ray((1, 2), (2, 3))
        assert isinstance(ray.anchor, planar.Vec2)
        assert_equal(ray.anchor, self.Vec2(1, 2))
        assert_equal(ray.direction, self.Vec2(2, 3).normalized())
        ray.anchor = (-3, 1)
        assert isinstance(ray.anchor, planar.Vec2)
        assert_equal(ray.anchor, self.Vec2(-3, 1))
        assert_equal(ray.direction, self.Vec2(2, 3).normalized())
        ray.anchor = self.Vec2(-11, -6)
        assert isinstance(ray.anchor, planar.Vec2)
        assert_equal(ray.anchor, self.Vec2(-11, -6))
        assert_equal(ray.direction, self.Vec2(2, 3).normalized())

    @raises(TypeError)
    def test_set_anchor_wrong_type(self):
        ray = self.Ray((1, 2), (2, 3))
        ray.anchor = 'yo'

    def test_line(self):
        ray = self.Ray((-3, 11), (-40, 1))
        line = ray.line
        assert isinstance(line, self.Line)
        assert_equal(line.direction, ray.direction)
        assert line.contains_point(ray.anchor)

    def test_points(self):
        ray = self.Ray((1, -5), (-1, 6))
        points = ray.points
        assert_equal(len(points), 2)
        assert points[0] != points[1]
        assert_equal(points[0], ray.anchor)
        assert ray.contains_point(points[1])

    def test_distance_to(self):
        line = self.Ray((-1, 1), (1, 1))
        assert_almost_equal(line.distance_to((0,0)), math.sqrt(2))
        assert_almost_equal(line.distance_to((0,1)), math.sqrt(2) / 2)
        assert_almost_equal(line.distance_to(self.Vec2(1,5)), math.sqrt(2))
        assert_almost_equal(line.distance_to((2, 4)), 0)
        assert_almost_equal(line.distance_to((-3, -1)), 2 * math.sqrt(2))

    def test_contains_point(self):
        import planar
        line = self.Ray((5, -2), (13, 7))
        assert line.contains_point((5, -2))
        assert line.contains_point((5, -2 + planar.EPSILON / 2))
        assert line.contains_point((5, -2 - planar.EPSILON / 2))
        assert line.contains_point((13 * 2000 + 5, 7 * 2000 - 2))
        assert line.contains_point(self.Vec2(5, -2))
        assert not line.contains_point((-8, -9))
        assert not line.contains_point((5, -2.01))
        assert not line.contains_point((5, -1.99))
        assert not line.contains_point(self.Vec2(0, 0))
        assert not line.contains_point((-100000, 50000))

    def test_point_behind(self):
        import planar
        ray = self.Ray((2, -3), (1, 20))
        assert ray.point_behind((2, -3 - planar.EPSILON * 2))
        assert ray.point_behind((1, -23))
        assert ray.point_behind((-10, -3.1))
        assert ray.point_behind(self.Vec2(10, -3.5))
        assert not ray.point_behind((2, -3))
        assert not ray.point_behind((3, 17))
        assert not ray.point_behind((3, -2))
        assert not ray.point_behind((1, -2))
        
    def test_point_right(self):
        import planar
        ray = self.Ray((-1,2), (-1,3))
        assert ray.point_right((0, 3))
        assert ray.point_right(self.Vec2(-0.9, 2.1))
        assert ray.point_right((10000, 5000))
        assert not ray.point_right((0, 0))
        assert not ray.point_right((-1.1, 2))
        assert not ray.point_right((-1,2))
        assert not ray.point_right(
            (-1 + planar.EPSILON / 2,2 + planar.EPSILON / 2))
        assert not ray.point_right((-4,8))
        assert not ray.point_right((-100000, -2000))

    def test_point_left(self):
        import planar
        ray = self.Ray((-3,-1), (40,1))
        assert ray.point_left((0, 0))
        assert ray.point_left((10000, 4000))
        assert not ray.point_left(self.Vec2(-3.1, -1))
        assert not ray.point_left((0, -1))
        assert not ray.point_left((-3, -1))
        assert not ray.point_left((-3 + planar.EPSILON / 2, -1))
        assert not ray.point_left((37, 0))
        assert not ray.point_left((-10000, -4000))

    def test_project_point(self):
        ray = self.Ray((0, 2), (1,1))
        assert ray.project((0,0)).almost_equals((0, 2))
        assert ray.project((-1,1)).almost_equals((0, 2))
        assert ray.project((-5,4)).almost_equals((0, 2))
        assert ray.project((0,4)).almost_equals((1, 3)),ray.project((0,4))
        assert ray.project(self.Vec2(3, 2)).almost_equals((1.5, 3.5))
        assert ray.project((-1,-3)).almost_equals((0,2))

    def test_transform(self):
        ray = self.Ray((0, 0), (2, 1))
        ray2 = ray * self.Affine.rotation(-90, pivot=(4, 2))
        assert isinstance(ray2, self.Ray)
        assert ray2 is not ray
        assert ray2.direction.almost_equals(
            self.Vec2(1, -2).normalized())
        assert ray2.contains_point((4, 2))

    def test_imul_transform(self):
        ray = orig = self.Ray((0, 0), (1, 1))
        ray *= self.Affine.translation((-1,1)) * self.Affine.scale((1, 0.5))
        assert ray is orig
        assert ray.direction.almost_equals(
            self.Vec2(1, 0.5).normalized())
        assert ray.contains_point((-1, 1))

    @raises(TypeError)
    def test_imul_incompatible(self):
        ray = self.Ray((0, 0), (1, 1)) 
        ray *= 2

    def test_equals(self):
        ray = self.Ray((1,-2), (2, 5))
        assert ray == ray
        assert ray == self.Ray((1,-2), (2, 5))
        assert not ray == self.Ray((1,-1), (2, 5))
        assert not ray == self.Ray((1, -2), (2, 4))
        assert not ray == None
        assert not ray == ((1,-2), (2, 5))

    def test_not_equals(self):
        ray = self.Ray((1,-2), (2, 5))
        assert not ray != ray
        assert not ray != self.Ray((1,-2), (2, 5))
        assert ray != self.Ray((3,-2), (2, 5))
        assert ray != self.Ray((1,-2), (0, 5))
        assert ray != None
        assert ray != ((1,-2), (2, 5))

    def test_almost_equals(self):
        ray = self.Ray((1,-2), (2, 5))
        assert ray.almost_equals(self.Ray.from_points([(1,-2), (5,8)]))
        assert ray.almost_equals(ray)
        assert not ray.almost_equals(self.Ray((1,-1.99), (2, 5)))

    def test_str(self):
        ray = self.Ray((0.37, 0), (0, 1))
        assert_equal(str(ray), "Ray((0.37, 0.0), (0.0, 1.0))")
        
    def test_repr(self):
        ray = self.Ray((0.37, 0), (0, 1))
        assert_equal(repr(ray), "Ray((0.37, 0.0), (0.0, 1.0))")


class BaseLineSegmentTestCase(LinearBaseTestCase):

    def test_null_direction(self):
        line = self.LineSegment((1,0), (0,0))
        assert_equal(line.length, 0)
        assert_equal(line.direction, self.Vec2(1, 0))

    @raises(TypeError)
    def test_from_normal_no_args(self):
        self.LineSegment.from_normal()

    @raises(TypeError)
    def test_from_normal_wrong_arg_types(self):
        self.LineSegment.from_normal(0, "baz", 0, 0)

    @raises(ValueError)
    def test_from_normal_null(self):
        self.LineSegment.from_normal((0,0), 1, 0, 0)

    def test_from_normal(self):
        line = self.LineSegment.from_normal((0.25,0.5), 3, -0.5, 1)
        assert_equal(line.direction, self.Vec2(-2,1).normalized())
        assert_equal(line.normal, self.Vec2(1,2).normalized())
        assert_equal(line.length, 1.5)

    def test_from_points_many_collinear(self):
        line = self.LineSegment.from_points(
            [(-7,-21), (-3,-9), (1, 3), (1003,3009), (5,15)])
        assert_equal(line.direction, self.Vec2(1,3).normalized())
        assert_equal(line.normal, self.Vec2(3,-1).normalized())
        assert_equal(line.anchor, self.Vec2(-7, -21))
        assert_equal(line.end, self.Vec2(1003, 3009))
        assert line.contains_point((0,0))

    def test_from_points_many_collinear_from_seq2(self):
        import planar
        line = self.LineSegment.from_points(
            planar.Seq2([(-7,-21), (-3,-9), (1, 3), (1003,3009), (5,15)]))
        assert_equal(line.direction, self.Vec2(1,3).normalized())
        assert_equal(line.normal, self.Vec2(3,-1).normalized())
        assert_equal(line.anchor, self.Vec2(-7, -21))
        assert_equal(line.end, self.Vec2(1003, 3009))
        assert line.contains_point((0,0))

    def test_from_points_degenerate(self):
        line = self.LineSegment.from_points([(2,1), (2,1), (2,1)])
        assert_equal(line.direction, self.Vec2(1,0))
        assert_equal(line.anchor, self.Vec2(2,1))
        assert_equal(line.end, self.Vec2(2,1))
        assert_equal(line.length, 0)

    def test_from_points_too_few_distinct(self):
        """Test is n/a to LineSegment"""

    @raises(ValueError)
    def test_from_points_too_few(self):
        self.LinearType.from_points([])

    def test_points(self):
        line = self.LineSegment((2,-3), (-1, 4.5))
        start, end = line.points
        assert_equal(start, self.Vec2(2, -3))
        assert_equal(end, self.Vec2(1, 1.5))

    def test_set_anchor(self):
        import planar
        line = self.LineSegment((2,-3), (-1, 4.5))
        line.anchor = (0, -2)
        assert isinstance(line.anchor, planar.Vec2)
        assert_almost_equal(line.anchor, self.Vec2(0, -2))
        assert_almost_equal(line.anchor, line.start)
        assert_almost_equal(line.end, self.Vec2(-1, 2.5))
        line.anchor = self.Vec2(2.5, 4)
        assert isinstance(line.anchor, planar.Vec2)
        assert_almost_equal(line.anchor, self.Vec2(2.5, 4))
        assert_almost_equal(line.end, self.Vec2(1.5, 8.5))
        assert_almost_equal(line.anchor, line.start)
        line.start = (0, 0)
        assert_almost_equal(line.start, self.Vec2(0, 0))
        assert_almost_equal(line.anchor, line.start)
        assert_almost_equal(line.end, self.Vec2(-1, 4.5))
        
    @raises(TypeError)
    def test_set_anchor_wrong_type(self):
        line = self.LineSegment((1, 2), (2, 3))
        line.anchor = 'yo'

    def test_set_vector(self):
        import planar
        line = self.LineSegment((5,-1), (-3, 3))
        assert_equal(line.vector, self.Vec2(-3, 3))
        line.vector = (7, -1)
        assert isinstance(line.vector, planar.Vec2)
        assert_equal(line.vector, self.Vec2(7, -1))
        assert_equal(line.start, self.Vec2(5, -1))
        assert_equal(line.end, self.Vec2(12, -2))
        line.vector = self.Vec2(0, 0)
        assert isinstance(line.vector, planar.Vec2)
        assert_equal(line.vector, self.Vec2(0, 0))
        assert_equal(line.start, self.Vec2(5, -1))
        assert_equal(line.end, self.Vec2(5, -1))
    
    @raises(TypeError)
    def test_set_vector_wrong_type(self):
        line = self.LineSegment((1, 2), (2, 3))
        line.vector = 'mama'
    
    def test_set_end(self):
        import planar
        line = self.LineSegment((5,-1), (-3, 3))
        assert_equal(line.end, self.Vec2(2, 2))
        line.end = (11, -3)
        assert isinstance(line.end, planar.Vec2)
        assert_equal(line.start, self.Vec2(5, -1))
        assert_equal(line.end, self.Vec2(11, -3))
        assert_equal(line.vector, self.Vec2(6, -2))
        line.end = self.Vec2(-1, -1)
        assert isinstance(line.end, planar.Vec2)
        assert_equal(line.start, self.Vec2(5, -1))
        assert_equal(line.end, self.Vec2(-1, -1))
        assert_equal(line.vector, self.Vec2(-6, 0))

    @raises(TypeError)
    def test_set_end_wrong_type(self):
        line = self.LineSegment((1, 2), (2, 3))
        line.end = None

    def test_mid(self):
        import planar
        line = self.LineSegment((-7, 3), (11, -6))
        assert isinstance(line.mid, planar.Vec2)
        assert_equal(line.mid, self.Vec2(-1.5, 0))

    def test_line(self):
        segment = self.LineSegment((-4,3), (11, -1))
        line = segment.line
        assert isinstance(line, self.Line)
        assert_equal(segment.direction, line.direction)
        assert line.contains_point(segment.start)
        assert line.contains_point(segment.end)

    def test_distance_to(self):
        line = self.LineSegment((-1, 1), (5, 5))
        assert_almost_equal(line.distance_to((0,0)), math.sqrt(2))
        assert_almost_equal(line.distance_to((-1,-2)), 3)
        assert_almost_equal(line.distance_to((0,1)), math.sqrt(2) / 2)
        assert_almost_equal(line.distance_to(
            self.Vec2(1,5)), (self.Vec2(1,5) - self.Vec2(2,4)).length)
        assert_almost_equal(line.distance_to((-0.5, 1.5)), 0)
        assert_almost_equal(line.distance_to((-3, -1)), 2 * math.sqrt(2))
        assert_almost_equal(line.distance_to((4, 8)), 2)

    def test_contains_point(self):
        import planar
        line = self.LineSegment((5, -2), (13, 7))
        assert line.contains_point((5, -2))
        assert line.contains_point((5, -2 + planar.EPSILON / 2))
        assert line.contains_point((5, -2 - planar.EPSILON / 2))
        assert line.contains_point((18, 5))
        assert line.contains_point((18, 5 + planar.EPSILON / 2))
        assert line.contains_point((11.5, 1.5))
        assert line.contains_point(self.Vec2(5, -2))
        assert not line.contains_point((-8, -9))
        assert not line.contains_point((5, -2.01))
        assert not line.contains_point((5, -1.99))
        assert not line.contains_point(self.Vec2(0, 0))
        assert not line.contains_point((-100000, 50000))

    def test_point_behind(self):
        import planar
        line = self.LineSegment((2, -3), (1, 20))
        assert line.point_behind((2, -3 - planar.EPSILON * 2))
        assert line.point_behind((1, -23))
        assert line.point_behind((-10, -3.1))
        assert line.point_behind(self.Vec2(10, -3.5))
        assert not line.point_behind((2, -3))
        assert not line.point_behind((3, 17))
        assert not line.point_behind((-2, 22))
        assert not line.point_behind((3, -2))
        assert not line.point_behind((1, -2))

    def test_point_ahead(self):
        import planar
        line = self.LineSegment((-20, -3), (19, 3))
        assert line.point_ahead((-1 + planar.EPSILON * 2, 0))
        assert line.point_ahead((0, 0))
        assert line.point_ahead((0, -3.1))
        assert line.point_ahead(self.Vec2(10, -3.5))
        assert not line.point_ahead((-2, -3))
        assert not line.point_ahead((-20, -3))
        assert not line.point_ahead(line.end)
        assert not line.point_ahead((-30, 0))

    def test_point_right(self):
        import planar
        line = self.LineSegment((-1,2), (-1,30))
        assert line.point_right((0, 3))
        assert line.point_right(self.Vec2(-0.9, 2.1))
        assert line.point_right((50, 10))
        assert not line.point_right((0, 0))
        assert not line.point_right((-1.1, 2))
        assert not line.point_right((-1,2))
        assert not line.point_right(
            (-1 + planar.EPSILON / 2,2 + planar.EPSILON / 2))
        assert not line.point_right((-4,8))
        assert not line.point_right((-100000, -2000))

    def test_point_left(self):
        import planar
        line = self.LineSegment((-3,-1), (40,1))
        assert line.point_left((0, 0))
        assert line.point_left((10, 400))
        assert not line.point_left(self.Vec2(-3.1, -1))
        assert not line.point_left((0, -1))
        assert not line.point_left((-3, -1))
        assert not line.point_left((-3 + planar.EPSILON / 2, -1))
        assert not line.point_left((37, 0))
        assert not line.point_left((-10000, -4000))

    def test_project_point(self):
        line = self.LineSegment((0, 2), (4,4))
        assert line.project((0,0)).almost_equals((0, 2))
        assert line.project((-1,1)).almost_equals((0, 2))
        assert line.project((-5,4)).almost_equals((0, 2))
        assert line.project((0,2)).almost_equals((0, 2))
        assert line.project((0,4)).almost_equals((1, 3)),line.project((0,4))
        assert line.project(self.Vec2(3, 2)).almost_equals((1.5, 3.5))
        assert line.project((-1,-3)).almost_equals((0,2))
        assert line.project((4,6)).almost_equals((4,6))
        assert line.project((5,6)).almost_equals((4,6))
        assert line.project((4.1, 6.1)).almost_equals((4,6))

    def test_transform(self):
        line = self.LineSegment((0, 0), (4, 2))
        line2 = line * self.Affine.rotation(-90, pivot=(4, 2))
        assert isinstance(line2, self.LineSegment)
        assert line2 is not line
        assert line2.direction.almost_equals(
            self.Vec2(1, -2).normalized())
        assert line2.vector.almost_equals((2, -4)), line2.vector
        assert line2.start.almost_equals((2, 6)), line2.start
        assert line2.end.almost_equals((4, 2))

    def test_imul_transform(self):
        line = orig = self.LineSegment((0, 0), (1, 1))
        line *= self.Affine.translation((-1,1)) * self.Affine.scale((1, 0.5))
        assert line is orig
        assert line.vector.almost_equals((1, 0.5)), line.vector
        assert line.start.almost_equals((-1, 1))
        assert line.end.almost_equals((0, 1.5)), line.end

    @raises(TypeError)
    def test_imul_incompatible(self):
        line = self.LineSegment((0, 0), (1, 1)) 
        line *= 2

    def test_equals(self):
        line = self.LineSegment((1,-2), (2, 5))
        assert line == line
        assert line == self.LineSegment((1,-2), (2, 5))
        assert not line == self.LineSegment((1,-1), (2, 5))
        assert not line == self.LineSegment((1, -2), (2, 4))
        assert not line == None
        assert not line == ((1,-2), (2, 5))

    def test_not_equals(self):
        line = self.LineSegment((1,-2), (2, 5))
        assert not line != line
        assert not line != self.LineSegment((1,-2), (2, 5))
        assert line != self.LineSegment((3,-2), (2, 5))
        assert line != self.LineSegment((1,-2), (0, 5))
        assert line != None
        assert line != ((1,-2), (2, 5))

    def test_almost_equals(self):
        line = self.LineSegment((1,-2), (2, 5))
        assert line.almost_equals(
            self.LineSegment.from_points([(1,-2), (3,3)]))
        assert line.almost_equals(line)
        assert not line.almost_equals(self.LineSegment((1,-1.99), (2, 5)))


class PyLineTestCase(LineBaseTestCase, unittest.TestCase):
    from planar.vector import Vec2
    from planar.line import Line
    from planar.transform import Affine
    LinearType = Line

    def test_str(self):
        line = self.Line((0.37, 0), (0, 1))
        assert_equal(str(line), "Line((0.37, 0.0), (0.0, 1.0))")
        
    def test_repr(self):
        line = self.Line((0.37, 0), (0, 1))
        assert_equal(repr(line), "Line((0.37, 0.0), (0.0, 1.0))")


class CLineTestCase(LineBaseTestCase, unittest.TestCase):
    from planar.c import Vec2, Line, Affine
    LinearType = Line

    def test_str(self):
        line = self.Line((0.37, 0), (0, 1))
        assert_equal(str(line), "Line((0.37, -0), (0, 1))")
        
    def test_repr(self):
        line = self.Line((0.37, 0), (0, 1))
        assert_equal(repr(line), "Line((0.37, -0), (0, 1))")


class PyRayTestCase(RayBaseTestCase, unittest.TestCase):
    from planar.vector import Vec2
    from planar.line import Ray, Line
    from planar.transform import Affine
    LinearType = Ray


class CRayTestCase(RayBaseTestCase, unittest.TestCase):
    from planar.c import Vec2, Ray, Line, Affine
    LinearType = Ray

    def test_str(self):
        ray = self.Ray((0.37, 0), (0, 1))
        assert_equal(str(ray), "Ray((0.37, 0), (0, 1))")
        
    def test_repr(self):
        ray = self.Ray((0.37, 0), (0, 1))
        assert_equal(repr(ray), "Ray((0.37, 0), (0, 1))")


class PySegmentTestCase(BaseLineSegmentTestCase, unittest.TestCase):
    from planar.vector import Vec2
    from planar.line import LineSegment, Line
    from planar.transform import Affine
    LinearType = LineSegment

    def test_str(self):
        line = self.LineSegment((0.37, 0), (2, 23.5))
        assert_equal(str(line), "LineSegment((0.37, 0.0), (2.0, 23.5))")
        
    def test_repr(self):
        line = self.LineSegment((0.37, 0), (2, 23.5))
        assert_equal(repr(line), "LineSegment((0.37, 0.0), (2.0, 23.5))")


class CSegmentTestCase(BaseLineSegmentTestCase, unittest.TestCase):
    from planar.c import Vec2, LineSegment, Line, Affine
    LinearType = LineSegment

    def test_str(self):
        line = self.LineSegment((0.37, 0), (2, 23.5))
        assert_equal(str(line), "LineSegment((0.37, 0), (2, 23.5))")
        
    def test_repr(self):
        line = self.LineSegment((0.37, 0), (2, 23.5))
        assert_equal(repr(line), "LineSegment((0.37, 0), (2, 23.5))")

if __name__ == '__main__':
    unittest.main()


# vim: ai ts=4 sts=4 et sw=4 tw=78

