"""Transform unit tests"""

from __future__ import division
import sys
import math
import unittest
from nose.tools import assert_equal, assert_almost_equal, raises

def tuple_almost_equal(t1, t2, error=0.00001):
    assert len(t1) == len(t2), "%r != %r" % (t1, t2)
    for m1, m2 in zip(t1, t2):
        assert abs(m1 - m2) <= error, "%r != %r" % (t1, t2)


class AffineBaseTestCase(object):

    @raises(TypeError)
    def test_zero_args(self):
        self.Affine()

    @raises(TypeError)
    def test_wrong_arg_type(self):
        self.Affine(None)

    @raises(TypeError)
    def test_args_too_few(self):
        self.Affine(1, 2)

    @raises(TypeError)
    def test_args_too_many(self):
        self.Affine(*range(10))

    @raises(TypeError)
    def test_args_members_wrong_type(self):
        self.Affine(0, 2, 3, None, None, "")

    def test_len(self):
        t = self.Affine(1, 2, 3, 4, 5, 6)
        assert_equal(len(t), 9)

    def test_slice_last_row(self):
        t = self.Affine(1, 2, 3, 4, 5, 6)
        assert_equal(t[-3:], (0, 0, 1))

    def test_members_are_floats(self):
        t = self.Affine(1, 2, 3, 4, 5, 6)
        for m in t:
            assert isinstance(m, float), repr(m)

    def test_str(self):
        assert_equal(
            str(self.Affine(1.111, 2.222, 3.333, -4.444, -5.555, 6.666)), 
            "| 1.11, 2.22, 3.33|\n|-4.44,-5.55, 6.67|\n| 0.00, 0.00, 1.00|")

    def test_repr(self):
        assert_equal(
            repr(self.Affine(1.111, 2.222, 3.456, 4.444, 5.5, 6)), 
            ("Affine(1.111, 2.222, 3.456,\n"
             "       4.444, 5.5, 6.0,\n"
             "       0.0, 0.0, 1.0)"))

    def test_identity_constructor(self):
        ident = self.Affine.identity()
        assert_equal(tuple(ident), (1,0,0, 0,1,0, 0,0,1))
        assert ident.is_identity

    def test_translation_constructor(self):
        trans = self.Affine.translation((2, -5))
        assert_equal(tuple(trans), (1,0,2, 0,1,-5, 0,0,1))
        trans = self.Affine.translation(self.Vec2(9, 8))
        assert_equal(tuple(trans), (1,0,9, 0,1,8, 0,0,1))

    def test_scale_constructor(self):
        scale = self.Affine.scale(5)
        assert_equal(tuple(scale), (5,0,0, 0,5,0, 0,0,1))
        scale = self.Affine.scale((-1, 2))
        assert_equal(tuple(scale), (-1,0,0, 0,2,0, 0,0,1))
        scale = self.Affine.scale(self.Vec2(3, 4))
        assert_equal(tuple(scale), (3,0,0, 0,4,0, 0,0,1))
        assert_equal(tuple(self.Affine.scale(1)), self.Affine.identity())

    def test_scale_constructor_with_anchor(self):
        scale = self.Affine.scale(5, anchor=(0,0))
        assert_equal(tuple(scale), (5,0,0, 0,5,0, 0,0,1))
        scale = self.Affine.scale(5, anchor=self.Vec2(2,1))
        assert_equal(tuple(scale), (5,0,8, 0,5,4, 0,0,1))
        scale = self.Affine.scale((3,4), self.Vec2(-10,3))
        assert_equal(tuple(scale), (3,0,-20, 0,4,9, 0,0,1))
        assert_equal(tuple(self.Affine.scale(1, (-10,3))), 
            tuple(self.Affine.identity()))

    def test_shear_constructor(self):
        shear = self.Affine.shear((2, 3))
        assert_equal(tuple(shear), (1,2,0, 3,1,0, 0,0,1))
        shear = self.Affine.shear(self.Vec2(-4, 2))
        assert_equal(tuple(shear), (1,-4,0, 2,1,0, 0,0,1))

    def test_shear_constructor_with_anchor(self):
        shear = self.Affine.shear((2, 3), anchor=(0, 0))
        assert_equal(tuple(shear), (1,2,0, 3,1,0, 0,0,1))
        shear = self.Affine.shear((2, 3), anchor=(-3, 2))
        assert_equal(tuple(shear), (1,2,4, 3,1,-9, 0,0,1))

    def test_rotation_constructor(self):
        rot = self.Affine.rotation(60)
        r = math.radians(60)
        s, c = math.sin(r), math.cos(r)
        assert_equal(tuple(rot), (c,s,0, -s,c,0, 0,0,1))
        rot = self.Affine.rotation(1743)
        r = math.radians(1743)
        s, c = math.sin(r), math.cos(r)
        assert_equal(tuple(rot), (c,s,0, -s,c,0, 0,0,1))
        assert_equal(tuple(self.Affine.rotation(0)), 
            tuple(self.Affine.identity()))
        tuple_almost_equal(tuple(self.Affine.rotation(90)), 
            (0,1,0, -1,0,0, 0,0,1))

    def test_rotation_constructor_with_pivot(self):
        assert_equal(tuple(self.Affine.rotation(60)),
            tuple(self.Affine.rotation(60, pivot=(0,0))))
        rot = self.Affine.rotation(27, pivot=self.Vec2(2,-4))
        r = math.radians(27)
        s, c = math.sin(r), math.cos(r)
        assert_equal(tuple(rot), 
            (c,s,c*2 + s*-4 - 2, -s,c,c*-4 - s*2 +4, 0,0,1))
        assert_equal(tuple(self.Affine.rotation(0, (-3, 2))), 
            tuple(self.Affine.identity()))

    def test_determinant(self):
        assert_equal(self.Affine.identity().determinant, 1)
        assert_equal(self.Affine.scale(2).determinant, 4)
        assert_equal(self.Affine.scale(0).determinant, 0)
        assert_equal(self.Affine.scale((5,1)).determinant, 5)
        assert_equal(self.Affine.scale((-1,1)).determinant, -1)
        assert_equal(self.Affine.scale((-1,0)).determinant, 0)
        assert_almost_equal(self.Affine.rotation(77).determinant, 1)
        assert_almost_equal(self.Affine.translation((32, -47)).determinant, 1)

    def test_is_rectilinear(self):
        assert self.Affine.identity().is_rectilinear
        assert self.Affine.scale((2.5, 6.1)).is_rectilinear
        assert self.Affine.translation((4, -1)).is_rectilinear
        assert self.Affine.rotation(90).is_rectilinear
        assert not self.Affine.shear((4, -1)).is_rectilinear
        assert not self.Affine.rotation(-26).is_rectilinear

    def test_is_degenerate(self):
        from planar import EPSILON
        assert not self.Affine.identity().is_degenerate
        assert not self.Affine.translation((2, -1)).is_degenerate
        assert not self.Affine.shear((0, -22.5)).is_degenerate
        assert not self.Affine.rotation(88.7).is_degenerate
        assert not self.Affine.scale(0.5).is_degenerate
        assert self.Affine.scale(0).is_degenerate
        assert self.Affine.scale((-10, 0)).is_degenerate
        assert self.Affine.scale((0, 300)).is_degenerate
        assert self.Affine.scale(0).is_degenerate
        assert self.Affine.scale(0).is_degenerate
        assert self.Affine.scale(EPSILON).is_degenerate

    def test_column_vectors(self):
        import planar
        a, b, c = self.Affine(2, 3, 4, 5, 6, 7).column_vectors
        assert isinstance(a, planar.Vec2)
        assert isinstance(b, planar.Vec2)
        assert isinstance(c, planar.Vec2)
        assert_equal(a, self.Vec2(2, 5))
        assert_equal(b, self.Vec2(3, 6))
        assert_equal(c, self.Vec2(4, 7))

    def test_almost_equals(self):
        from planar import EPSILON
        assert EPSILON != 0, EPSILON
        E = EPSILON * 0.5
        t = self.Affine(1.0, E, 0, -E, 1.0+E, E)
        assert t.almost_equals(self.Affine.identity())
        assert self.Affine.identity().almost_equals(t)
        assert t.almost_equals(t)
        t = self.Affine(1.0, 0, 0, -EPSILON, 1.0, 0)
        assert not t.almost_equals(self.Affine.identity())
        assert not self.Affine.identity().almost_equals(t)
        assert t.almost_equals(t)

    def test_equality(self):
        t1 = self.Affine(1, 2, 3, 4, 5, 6)
        t2 = self.Affine(6, 5, 4, 3, 2, 1)
        t3 = self.Affine(1, 2, 3, 4, 5, 6)
        assert t1 == t3
        assert not t1 == t2
        assert t2 == t2
        assert not t1 != t3
        assert not t2 != t2
        assert t1 != t2
        assert not t1 == 1
        assert t1 != 1

    @raises(TypeError)
    def test_gt(self):
        self.Affine(1,2,3,4,5,6) > self.Affine(6,5,4,3,2,1)

    @raises(TypeError)
    def test_lt(self):
        self.Affine(1,2,3,4,5,6) < self.Affine(6,5,4,3,2,1)

    @raises(TypeError)
    def test_add(self):
        self.Affine(1,2,3,4,5,6) + self.Affine(6,5,4,3,2,1)
        
    @raises(TypeError)
    def test_sub(self):
        self.Affine(1,2,3,4,5,6) - self.Affine(6,5,4,3,2,1)


class PyAffineTestCase(AffineBaseTestCase, unittest.TestCase):
    from planar.transform import Affine
    from planar.vector import Vec2


if __name__ == '__main__':
    unittest.main()


# vim: ai ts=4 sts=4 et sw=4 tw=78

