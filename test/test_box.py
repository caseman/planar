"""BoundingBox class unit tests"""

from __future__ import division
import sys
import math
import unittest
from nose.tools import assert_equal, assert_almost_equal, raises


class BoundingBoxBaseTestCase(object):

    @raises(TypeError)
    def test_too_few_args(self):
        self.BoundingBox()

    @raises(ValueError)
    def test_no_points(self):
        self.BoundingBox([])
    
    def test_one_point(self):
        box = self.BoundingBox([(2,4)])
        assert_equal(box.max_point, self.Vec2(2, 4))
        assert_equal(box.min_point, self.Vec2(2, 4))
    
    def test_two_points_already_min_max(self):
        box = self.BoundingBox([(-2, -1), (3, 4)])
        assert_equal(box.max_point, self.Vec2(3, 4))
        assert_equal(box.min_point, self.Vec2(-2, -1))
    
    def test_two_points_not_min_max(self):
        box = self.BoundingBox([self.Vec2(2, -4), self.Vec2(-3, -1)])
        assert_equal(box.min_point, self.Vec2(-3, -4))
        assert_equal(box.max_point, self.Vec2(2, -1))
    
    def test_many_points(self):
        box = self.BoundingBox(((i, 10000 - i) for i in range(10000)))
        assert_equal(box.min_point, (0, 1))
        assert_equal(box.max_point, (9999, 10000))
    
    def test_from_points(self):
        box = self.BoundingBox.from_points([(0,2), (1,-3), (-1,0)])
        assert_equal(box.min_point, (-1, -3))
        assert_equal(box.max_point, (1, 2))
    
    def test_from_Seq2(self):
        box = self.BoundingBox(self.Seq2([(9,0), (-1, 0), (4, -1)]))
        assert_equal(box.min_point, (-1, -1))
        assert_equal(box.max_point, (9, 0))
    
    def test_bounding_box(self):
        box = self.BoundingBox([(-2, -1), (3, 4)])
        box2 = box.bounding_box
        assert isinstance(box2, self.BoundingBox)
        assert_equal(box.min_point, box2.min_point)
        assert_equal(box.max_point, box2.max_point)
    
    def test_min_point_max_point(self):
        import planar
        box = self.BoundingBox([(-2, -1), (3, 4)])
        assert isinstance(box.max_point, planar.Vec2)
        assert_equal(box.max_point, self.Vec2(3, 4))
        assert isinstance(box.min_point, planar.Vec2)
        assert_equal(box.min_point, self.Vec2(-2, -1))
        
    @raises(AttributeError)
    def test_immutable_min_point(self):
        import planar
        box = self.BoundingBox([(-2, -1), (3, 4)])
        box.min_point = self.Vec2(4,3)
        
    @raises(AttributeError)
    def test_immutable_max_point(self):
        import planar
        box = self.BoundingBox([(-2, -1), (3, 4)])
        box.max_point = self.Vec2(4,3)
    
    def test_center(self):
        import planar
        box = self.BoundingBox([(-3, -1), (1, 4)])
        assert isinstance(box.center, planar.Vec2)
        assert_equal(box.center, planar.Vec2(-1, 1.5))
        assert_equal(self.BoundingBox([(8, 12)]).center, planar.Vec2(8, 12))
    
    def test_width_height(self):
        box = self.BoundingBox([(-2, -3.5), (3, 4)])
        assert_equal(box.width, 5)
        assert_equal(box.height, 7.5)
    
    def test_is_empty(self):
        assert not self.BoundingBox([(-2, -3.5), (3, 4)]).is_empty
        assert self.BoundingBox([(-2, -3.5), (-2, 4)]).is_empty
        assert self.BoundingBox([(-2, 4), (3, 4)]).is_empty
        assert self.BoundingBox([(1, 1), (1, 1)]).is_empty

    def test_from_shapes(self):
        BoundingBox = self.BoundingBox
        class Shape(object):
            def __init__(self, x1, y1, x2, y2):
                self.bounding_box = BoundingBox([(x1, y1), (x2, y2)])
        shapes = [
            Shape(0, 0, 10, 4),
            Shape(-2, 4, -1, 5),
            Shape(20, 2, 25, 2.5),
            Shape(-5, -5, -5, -5),
            Shape(-2, -2, 2, 2),
        ]
        box = self.BoundingBox.from_shapes(shapes)
        assert_equal(box.min_point, (-5, -5))
        assert_equal(box.max_point, (25, 5))

        box = self.BoundingBox.from_shapes(iter(shapes))
        assert_equal(box.min_point, (-5, -5))
        assert_equal(box.max_point, (25, 5))

    @raises(ValueError)
    def test_from_shapes_no_shapes(self):
        box = self.BoundingBox.from_shapes([])
    
    def test_from_center(self):
        box = self.BoundingBox.from_center((2, 3), 14, 3)
        assert_equal(box.min_point, (-5, 1.5))
        assert_equal(box.max_point, (9, 4.5))
        assert_equal(box.width, 14)
        assert_equal(box.height, 3)

        box = self.BoundingBox.from_center(self.Vec2(0, -4), 20, -6)
        assert_equal(box.min_point, (-10, -7))
        assert_equal(box.max_point, (10, -1))
        assert_equal(box.width, 20)
        assert_equal(box.height, 6)
    
    @raises(TypeError)
    def test_from_center_bad_args(self):
        self.BoundingBox.from_center(0, 1, 1)
    
    def test_inflate_scalar(self):
        box1 = self.BoundingBox([(3, 1), (5, 6)])
        box2 = box1.inflate(1)
        assert box2 is not box1
        assert_equal(box1.width, 2)
        assert_equal(box1.height, 5)
        assert_equal(box2.width, 3)
        assert_equal(box2.height, 6)
        assert_equal(box2.center, box1.center)
        box3 = box2.inflate(-2.5)
        assert box3 is not box2
        assert_equal(box1.width, 2)
        assert_equal(box1.height, 5)
        assert_equal(box2.width, 3)
        assert_equal(box2.height, 6)
        assert_equal(box2.center, box1.center)
        assert_equal(box3.width, 0.5)
        assert_equal(box3.height, 3.5)
        assert_equal(box3.center, box2.center)
    
    def test_inflate_vector(self):
        box1 = self.BoundingBox([(-2, 0), (7, 1.5)])
        box2 = box1.inflate((-3, 1.5))
        assert box2 is not box1
        assert_equal(box1.width, 9)
        assert_equal(box1.height, 1.5)
        assert_equal(box2.width, 6)
        assert_equal(box2.height, 3)
        assert_equal(box2.center, box1.center)
    
    @raises(ValueError)
    def test_inflate_bad_arg(self):
        self.BoundingBox([(3, 1), (5, 6)]).inflate('badbad')
        
    def test_contains_point(self):
        box = self.BoundingBox([(-1, -2), (3, 0)])
        assert box.contains((0, 0))
        assert box.contains((-0.5, -1))
        assert box.contains(self.Vec2(-1, -2))
        assert box.contains((3, 0))
        assert box.contains((-1, 0))
        assert box.contains((3, -2))
        assert not box.contains((-1.1, -2))
        assert not box.contains(self.Vec2(3.1, 0))
        assert not box.contains((-50, 0))
        assert not box.contains((50, 0))
        assert not box.contains((0, 50))
        assert not box.contains((50, 50))
    
    def test_contains_shape(self):
        BoundingBox = self.BoundingBox
        class Shape(object):
            def __init__(self, x1, y1, x2, y2):
                self.bounding_box = BoundingBox([(x1, y1), (x2, y2)])
        box = self.BoundingBox([(2, 6), (5, 7)])
        assert box.contains(Shape(2, 6, 5, 7))
        assert box.contains(Shape(2.5, 6.25, 4.5, 6.5))
        assert box.contains(Shape(3, 6.5, 3, 6.5))
        assert not box.contains(Shape(1, 4, 3, 6.5))
        assert not box.contains(Shape(3, 6.5, 6, 8))
        assert not box.contains(Shape(3, 6.5, 0, 0))
        assert not box.contains(Shape(1, 5, 6, 8))
        assert not box.contains(Shape(10, 50, 15, 80))
    
    @raises(TypeError)
    def test_contains_wrong_type(self):
        self.BoundingBox([(2, 6), (5, 7)]).contains(None)

    def test_fit_box(self):
        box = self.BoundingBox([(-1, 2), (4, 5)])
        frame = self.BoundingBox([(0, 0), (50, 50)])
        fitted = frame.fit(box)
        assert fitted is not box
        assert fitted is not frame
        assert_equal(fitted.width, 50)
        assert_equal(fitted.height, 30)
        assert_equal(fitted.center, frame.center)
        frame = self.BoundingBox([(-100, -50), (-60, -44)])
        fitted = frame.fit(box)
        assert_equal(fitted.width, 10)
        assert_equal(fitted.height, 6)
        assert_equal(fitted.center, frame.center)

    def test_fit_transformable_shape(self):
        import planar
        BoundingBox = self.BoundingBox
        class Shape(object):
            def __init__(self, x1, y1, x2, y2):
                self.bounding_box = BoundingBox([(x1, y1), (x2, y2)])
            def __mul__(self, other):
                assert isinstance(other, planar.Affine)
                self.xform = other
                return self

        shape = Shape(10, -2, 14, 1)
        frame = self.BoundingBox([(-4, 1), (4, -10)])
        shape2 = frame.fit(shape)
        xv, yv, tv = shape2.xform.column_vectors
        assert_equal(xv, (2, 0))
        assert_equal(yv, (0, 2))
        assert_equal(tv, frame.center - shape2.bounding_box.center)

    @raises(ValueError)
    def test_fit_wrong_arg_type(self):
        self.BoundingBox([(0, 0), (40, 40)]).fit(None)


class PyBoundingBoxTestCase(BoundingBoxBaseTestCase, unittest.TestCase):
    from planar.vector import Vec2, Seq2
    from planar.box import BoundingBox


class CBoundingBoxTestCase(BoundingBoxBaseTestCase, unittest.TestCase):
    from planar.c import Vec2, Seq2, BoundingBox


if __name__ == '__main__':
    unittest.main()


# vim: ai ts=4 sts=4 et sw=4 tw=78

