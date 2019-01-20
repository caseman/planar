"""Shape operation unit tests"""

from __future__ import division
import math
import unittest
from nose.tools import assert_equal, assert_almost_equal, raises


class ShapeOpTestCase(object):

    def boxes(self):
        return [self.BoundingBox(((-2,0), (-1,1))),
                self.BoundingBox(((-2,1), (-1,2))),
                self.BoundingBox(((-2,1), (-1,2))),
                self.BoundingBox(((0,-0.5), (3,-0.0001))),
                self.BoundingBox(((2.5,0.5), (3.5,0.6))),
                self.BoundingBox(((-1,-2), (3,-0.1)))]

    def test_bbox_encloses_bbox_disjoint(self):
        b1 = self.BoundingBox(((0,0), (2,1)))
        for b2 in self.boxes():
            assert not self.op.bbox_encloses_bbox(b1, b2)

    def test_bbox_encloses_bbox_intersecting(self):
        b1 = self.BoundingBox(((-1.5,0), (2,3)))
        for b2 in self.boxes():
            assert not self.op.bbox_encloses_bbox(b1, b2)

    def test_bbox_encloses_bbox_enclosing(self):
        b1 = self.BoundingBox(((-2,-2), (4,3)))
        for b2 in self.boxes():
            assert self.op.bbox_encloses_bbox(b1, b2)

    def test_bbox_collides_bbox_disjoint(self):
        b1 = self.BoundingBox(((0,0), (2,1)))
        for b2 in self.boxes():
            assert not self.op.bbox_collides_bbox(b1, b2)

    def test_bbox_collides_bbox_intersecting(self):
        b1 = self.BoundingBox(((-1.5,-0.15), (2.5,3)))
        for b2 in self.boxes():
            assert self.op.bbox_collides_bbox(b1, b2)

    def test_bbox_collides_bbox_enclosing(self):
        b1 = self.BoundingBox(((-2,-2), (4,3)))
        for b2 in self.boxes():
            assert self.op.bbox_collides_bbox(b1, b2)

    def test_bbox_collides_bbox_touching_below_left(self):
        b1 = self.BoundingBox(((-1.5,-0.15), (2.5,3)))
        assert not self.op.bbox_collides_bbox(b1, 
            self.BoundingBox(((-2,0), (-1.5,0))))
        assert not self.op.bbox_collides_bbox(b1, 
            self.BoundingBox(((-2,-0.5), (2,-0.15))))
        assert not self.op.bbox_collides_bbox(b1, 
            self.BoundingBox(((-2,-0.5), (-1.5,-0.15))))
        assert not self.op.bbox_collides_bbox(b1, 
            self.BoundingBox(((-2,3), (-1.5,3.5))))

    def test_bbox_collides_bbox_touching_above_right(self):
        b1 = self.BoundingBox(((-1.5,-0.15), (2.5,3)))
        assert self.op.bbox_collides_bbox(b1, 
            self.BoundingBox(((2.5,2), (3.5,2.9))))
        assert self.op.bbox_collides_bbox(b1, 
            self.BoundingBox(((2.5,3), (2.7,3.1))))
        assert self.op.bbox_collides_bbox(b1, 
            self.BoundingBox(((2.5,3), (3,4))))


class PyShapeOpTestCase(ShapeOpTestCase, unittest.TestCase):
    from planar import shape_op as op
    from planar.py import BoundingBox

"""
class CShapeOpTestCase(BoundingBoxBaseTestCase, unittest.TestCase):
    from planar.c import 
"""

if __name__ == '__main__':
    unittest.main()


# vim: ai ts=4 sts=4 et sw=4 tw=78

