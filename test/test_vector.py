"""Vector class unit tests"""

from __future__ import division
import sys
import math
import unittest
from nose.tools import assert_equal, assert_almost_equal, raises


class Vec2BaseTestCase(object):

    @raises(TypeError)
    def test_too_few_args_zero(self):
        self.Vec2()

    @raises(TypeError)
    def test_too_few_args_one(self):
        self.Vec2(42)

    @raises(TypeError)
    def test_too_many_args(self):
        self.Vec2(1, 2, 3, 4)

    @raises(TypeError)
    def test_wrong_arg_type(self):
        self.Vec2('2', 'arg')

    def test_polar(self):
        v = self.Vec2.polar(60)
        assert isinstance(v, self.Vec2)
        assert_almost_equal(v.angle, 60)
        assert_almost_equal(v.length, 1.0)
        assert_almost_equal(v.x, math.cos(math.radians(60)))
        assert_almost_equal(v.y, math.sin(math.radians(60)))
        
        v2 = self.Vec2.polar(-90, 10)
        assert_almost_equal(v2.length, 10)
        assert_equal(v2.angle, -90)
        assert_equal(v2.x, 0)
        assert_equal(v2.y, -10)

        assert_equal(self.Vec2.polar(10, 10), 
            self.Vec2.polar(angle=10, length=10))

        assert_almost_equal(self.Vec2.polar(361).angle, 1)

    def test_polar_quadrants(self):
        assert_equal(tuple(self.Vec2.polar(0)), (1, 0))
        assert_equal(tuple(self.Vec2.polar(90)), (0, 1))
        assert_equal(tuple(self.Vec2.polar(180)), (-1, 0))
        assert_equal(tuple(self.Vec2.polar(-180)), (-1, 0))
        assert_equal(tuple(self.Vec2.polar(270)), (0, -1))
        assert_equal(tuple(self.Vec2.polar(-90)), (0, -1))
        assert_equal(tuple(self.Vec2.polar(360)), (1, 0))
        assert_equal(tuple(self.Vec2.polar(450)), (0, 1))
        assert_equal(tuple(self.Vec2.polar(-450)), (0, -1))

    @raises(TypeError)
    def test_polar_bad_angle(self):
        self.Vec2.polar('44')

    @raises(TypeError)
    def test_polar_bad_length(self):
        self.Vec2.polar(0, 'yikes')

    def test_members_are_floats(self):
        x, y = self.Vec2(1, 5)
        assert isinstance(x, float)
        assert isinstance(y, float)

    @raises(TypeError)
    def test_immutable_members(self):
        v = self.Vec2(1, 1)
        v[0] = 0

    def test_len(self):
        assert_equal(len(self.Vec2(1, 1)), 2)

    def test_str(self):
        assert_equal(str(self.Vec2(-3.5, 4.446)), 'Vec2(-3.50, 4.45)')

    def test_repr(self):
        assert_equal(repr(self.Vec2(-3.5, 4.444)), 'Vec2(-3.5, 4.444)')

    def test_coords(self):
        v = self.Vec2(1, 3)
        assert v.x == v[0] == 1
        assert v.y == v[1] == 3

    @raises(AttributeError)
    def test_immutable_x(self):
        v = self.Vec2(1, 3)
        v.x = 4
        
    @raises(AttributeError)
    def test_immutable_y(self):
        v = self.Vec2(1, 3)
        v.y = -2

    def test_length2(self):
        v = self.Vec2(2, 3)
        assert_equal(v.length2, 13)
        # do the assert again to test the cache
        assert_equal(v.length2, 13)

    def test_length(self):
        v = self.Vec2(3, 4)
        assert_equal(v.length, 5)
        # do the assert again to test the cache
        assert_equal(v.length, 5)

    def test_is_null(self):
        from planar import EPSILON
        assert self.Vec2(0, 0).is_null
        assert self.Vec2(EPSILON / 2, -EPSILON / 2).is_null
        assert not self.Vec2(EPSILON, 0).is_null
        assert not self.Vec2(1, 0).is_null
        assert not self.Vec2(0, -0.1).is_null
        assert not self.Vec2(float('nan'), 0).is_null

    def test_almost_equals(self):
        from planar import EPSILON
        v = self.Vec2(-1, 56)
        assert v.almost_equals(v)
        assert v.almost_equals(self.Vec2(-1 + EPSILON/2, 56))
        assert v.almost_equals(self.Vec2(-1 - EPSILON/2, 56))
        assert v.almost_equals(self.Vec2(-1, 56 - EPSILON/2))
        assert not v.almost_equals(self.Vec2(-1 - EPSILON, 56))
        assert not v.almost_equals(self.Vec2(-1, 56 + EPSILON))
        assert not v.almost_equals(self.Vec2(1, 56))

    def test_angle(self):
        assert_equal(self.Vec2(1,0).angle, 0)
        assert_equal(self.Vec2(0,1).angle, 90)
        assert_equal(self.Vec2(1,1).angle, 45)
        assert_equal(self.Vec2(-1,0).angle, 180)
        assert_equal(self.Vec2(0,-1).angle, -90)
        assert_equal(self.Vec2(-1,-1).angle, -135)

    def test_angle_to(self):
        assert_almost_equal(self.Vec2(1,1).angle_to(self.Vec2(1,1)), 0)
        assert_almost_equal(self.Vec2(1,1).angle_to(self.Vec2(0,1)), 45)
        assert_almost_equal(self.Vec2(1,1).angle_to(self.Vec2(1,0)), -45)
        assert_almost_equal(self.Vec2(1,0).angle_to(self.Vec2(1,1)), 45)
        assert_almost_equal(self.Vec2(1,-1).angle_to(self.Vec2(1,1)), 90)
        assert_almost_equal(self.Vec2(1,1).angle_to(self.Vec2(-1,-1)), -180)

    def test_normalized(self):
        n = self.Vec2(1,1).normalized()
        assert_almost_equal(n.length, 1)
        assert_almost_equal(n.x, 1 / math.sqrt(2))
        assert_almost_equal(n.y, 1 / math.sqrt(2))

        n = self.Vec2(10, 0).normalized()
        assert_almost_equal(n.length, 1)
        assert_almost_equal(n.x, 1)
        assert_almost_equal(n.y, 0)

        assert_equal(self.Vec2(0, 0).normalized(), self.Vec2(0, 0))

    def test_perpendicular(self):
        assert_equal(self.Vec2(10,0).perpendicular(), self.Vec2(0, 10))
        assert_equal(self.Vec2(2,2).perpendicular(), self.Vec2(-2, 2))

    def test_dot(self):
        v1 = self.Vec2.polar(60, 5)
        v2 = self.Vec2.polar(80, 7)
        assert_almost_equal(v1.dot(v2), 5 * 7 * math.cos(math.radians(20)))

    def test_cross(self):
        v1 = self.Vec2.polar(10, 4)
        v2 = self.Vec2.polar(35, 6)
        assert_almost_equal(v1.cross(v2), 4 * 6 * math.sin(math.radians(25)))

    def test_distance_to(self):
        assert_equal(self.Vec2(3,0).distance_to(self.Vec2(0,4)), 5)

    def test_rotated(self):
        assert_almost_equal(self.Vec2.polar(45).rotated(22).angle, 67)
        assert_almost_equal(self.Vec2.polar(70).rotated(-15).angle, 55)
        assert_equal(self.Vec2(1, 0).rotated(90).angle, 90)

    def test_scaled_to(self):
        v = self.Vec2.polar(77, 50)
        assert_almost_equal(v.scaled_to(15).length, 15)
        assert_almost_equal(v.scaled_to(5).length2, 25)
        assert_equal(self.Vec2(0, 0).scaled_to(100), self.Vec2(0, 0))

    def test_project(self):
        assert_equal(
            self.Vec2(4, 0).project(self.Vec2(2, 1)), self.Vec2(2, 0))
        assert_equal(
            self.Vec2(0, 0).project(self.Vec2(2, 2)), self.Vec2(0, 0))
    
    def test_reflect(self):
        assert_equal(
            self.Vec2(2, -2).reflect(self.Vec2(3, 0)), self.Vec2(2, 2))
        assert_equal(
            self.Vec2(2, -2).reflect(self.Vec2(1, 0)), self.Vec2(2, 2))
        assert_equal(
            self.Vec2(3, 1).reflect(self.Vec2(-1, -1)), self.Vec2(1,3))
        assert_equal(
            self.Vec2(0, 0).reflect(self.Vec2(1, 1)), self.Vec2(0,0))
        assert_equal(
            self.Vec2(1, 1).reflect(self.Vec2(0, 0)), self.Vec2(0,0))

    def test_clamped(self):
        v = self.Vec2(30, 40)
        clamped = v.clamped(max_length=5)
        assert_equal(clamped.length, 5)
        assert_equal(clamped, self.Vec2(3, 4))
        assert_equal(
            self.Vec2(3, 4).clamped(min_length=50), self.Vec2(30, 40))
        assert_equal(v.clamped(40, 60), v)
        assert_equal(v.clamped(50, 50), v)
        assert_equal(self.Vec2(0,0).clamped(min_length=20), self.Vec2(0,0))

    def test_lerp(self):
        v1 = self.Vec2(1, 1)
        v2 = self.Vec2(3, 2)
        assert_equal(v1.lerp(v2, 0.5), self.Vec2(2, 1.5))
        assert_equal(v1.lerp(v2, 0), v1)
        assert_equal(v1.lerp(v2, 1), v2)
        assert_equal(v1.lerp(v2, 2), v2 * 2 - v1)
        assert_equal(v1.lerp(v2, -1), v1 * 2 - v2)

    def test_comparison(self):
        v1 = self.Vec2(1, 2)
        v2 = self.Vec2(2, 3)
        assert v1 == v1
        assert v1 != v2
        assert v1 >= v1
        assert not v1 < v1
        assert not v1 > v1
        assert v2 >= v1
        assert v2 > v1
        assert not v1 > v2
        assert v1 <= v1
        assert v1 <= v2
        assert v1 < v2

    def test_comparison_casts(self):
        assert self.Vec2(6.2, 3) == (6.2, 3)
        assert (6.2, 3) == self.Vec2(6.2, 3)
        assert not self.Vec2(6.2, 3) == (6.2, 3.2)
        assert self.Vec2(6.2, 3) != (6.2, 3.2)
        assert (6.2, 3.2) != self.Vec2(6.2, 3)
        assert self.Vec2(6.2, 3) != (6.2, 3, 2)
        assert not self.Vec2(6.2, 3) == (6.2, 3, 2)
        assert self.Vec2(6.2, 3) != (6.2,)
        assert self.Vec2(6.2, 3) != 6.2
        assert self.Vec2(6.2, 3) != None
        assert not self.Vec2(6.2, 3) == None
        assert self.Vec2(6.2, 3) != ()
        assert not self.Vec2(6.2, 3) == ()
        assert None != self.Vec2(6.2, 3)
        assert self.Vec2(8, 1) == [8, 1]
        assert [8, 1] == self.Vec2(8, 1)
        assert self.Vec2(8, 1) != set([8, 1])
        assert self.Vec2(8, 1) != [8, 1, 0]
        assert self.Vec2(8, 1) != [8]
        assert not self.Vec2(8, 1) == []
        assert self.Vec2(8, 1) != []

    @raises(TypeError)
    def test_comparison_cast_unordered_gt(self):
        self.Vec2(2, 3) > 3

    @raises(TypeError)
    def test_comparison_cast_unordered_ge(self):
        self.Vec2(2, 3) >= 3

    @raises(TypeError)
    def test_comparison_cast_unordered_lt(self):
        self.Vec2(2, 3) < 3

    @raises(TypeError)
    def test_comparison_cast_unordered_le(self):
        self.Vec2(2, 3) <= 3

    def test_comparison_subclass(self):
        class V(self.Vec2): pass
        assert self.Vec2(5, 4) == V(5, 4)
        assert V(5, 4) == self.Vec2(5, 4)
        assert self.Vec2(5, 4) != V(4, 4)
        assert V(4, 4) != self.Vec2(5, 4)

    def test_add(self):
        assert_equal(self.Vec2(1, 2) + self.Vec2(3, 4), self.Vec2(4, 6))
        v = self.Vec2(2, 2)
        v += self.Vec2(1, 0)
        assert_equal(v, self.Vec2(3, 2))

    @raises(TypeError)
    def test_add_wrong_len(self):
        self.Vec2(-1, 5) + (3, 4, 5)

    def test_sub(self):
        assert_equal(self.Vec2(3, 3) - self.Vec2(1, 4), self.Vec2(2, -1))
        v = self.Vec2(-1, 3)
        v -= self.Vec2(3, 3)
        assert_equal(v, self.Vec2(-4, 0))

    @raises(TypeError)
    def test_sub_wrong_len(self):
        self.Vec2(-1, 5) - (3, 4, 5)

    def test_mul(self):
        assert_equal(self.Vec2(2, 3) * 2, self.Vec2(4, 6))
        assert_equal(3 * self.Vec2(2, 1), self.Vec2(6, 3))
        assert_equal(self.Vec2(5, 2) * self.Vec2(0, -1), self.Vec2(0, -2))
        v = self.Vec2(3, 2)
        v *= 4
        assert_equal(v, self.Vec2(12, 8))
        v *= self.Vec2(-1, 2)
        assert_equal(v, self.Vec2(-12, 16))

    @raises(TypeError)
    def test_mul_wrong_len(self):
        self.Vec2(-1, 5) * (3, 4, 5)

    def test_truediv(self):
        assert_equal(self.Vec2(1, 4) / 2, self.Vec2(0.5, 2))
        assert_equal(6 / self.Vec2(1, 4), self.Vec2(6, 1.5))
        assert_equal(self.Vec2(1, 4) / self.Vec2(4, 2), self.Vec2(0.25, 2))
        assert_equal(self.Vec2(1, 4) / (4, 2), self.Vec2(0.25, 2))
        assert_equal((1, 4) / self.Vec2(4, 2), self.Vec2(0.25, 2))
        v = self.Vec2(6, 3)
        v /= 3
        assert_equal(v, self.Vec2(2, 1))

    @raises(TypeError)
    def test_truediv_wrong_len(self):
        self.Vec2(-1, 5) / (3, 4, 5)

    @raises(TypeError)
    def test_rtruediv_wrong_len(self):
        (3, 4, 5) / self.Vec2(-1, 5)

    def test_floordiv(self):
        assert_equal(self.Vec2(1, 4) // 2, self.Vec2(0, 2))
        assert_equal(5 // self.Vec2(2, 4), self.Vec2(2, 1))
        assert_equal(self.Vec2(1, 4) // self.Vec2(4, 2), self.Vec2(0, 2))
        assert_equal(self.Vec2(1, 4) // (4, 2), self.Vec2(0, 2))
        assert_equal((1, 4) // self.Vec2(4, 2), self.Vec2(0, 2))
        v = self.Vec2(6, 2)
        v //= 3
        assert_equal(v, self.Vec2(2, 0))

    @raises(TypeError)
    def test_floordiv_wrong_len(self):
        self.Vec2(-1, 5) // (3, 4, 5)

    @raises(TypeError)
    def test_rfloordiv_wrong_len(self):
        (3, 4, 5) // self.Vec2(-1, 5)

    def test_div_by_zero(self):
        for a, b in [
            (self.Vec2(1, 2), self.Vec2(0, 0)),
            (self.Vec2(1, 2), self.Vec2(1, 0)),
            (self.Vec2(1, 2), self.Vec2(0, 1)),
            (self.Vec2(1, 2), 0),
            (5, self.Vec2(0, 0)),
            (5, self.Vec2(1, 0)),
            (5, self.Vec2(0, 1)),]:
            try: a / b
            except ZeroDivisionError: pass
            else: 
                self.fail("Expected ZeroDivisionError for: %r / %r" % (a, b))
            try: a // b
            except ZeroDivisionError: pass
            else: 
                self.fail("Expected ZeroDivisionError for: %r // %r" % (a, b))

    def test_neg(self):
        assert_equal(-self.Vec2(5,6), self.Vec2(-5,-6))

    def test_pos(self):
        assert_equal(+self.Vec2(-1,0), self.Vec2(-1,0))

    def test_abs(self):
        assert_equal(abs(self.Vec2(3, 4)), 5)
        assert_equal(abs(self.Vec2(-3, 4)), 5)

    def test_bool(self):
        assert self.Vec2(0.1, 0)
        assert self.Vec2(0, 0.1)
        assert self.Vec2(0.1, 0.1)
        assert not self.Vec2(0, 0)
    
    def test_hash(self):
        assert hash(self.Vec2(0,0)) != hash(self.Vec2(1,0))
        assert hash(self.Vec2(0,1)) != hash(self.Vec2(1,0))
        assert hash(self.Vec2(1,1)) == hash(self.Vec2(1,1))
        s = set([self.Vec2(1,1), self.Vec2(1,0), self.Vec2(0,1)])
        assert self.Vec2(1,1) in s
        assert self.Vec2(1,0) in s
        assert self.Vec2(0,1) in s
        assert self.Vec2(0,0) not in s


class PyVec2TestCase(Vec2BaseTestCase, unittest.TestCase):
    from planar.vector import Vec2


class CVec2TestCase(Vec2BaseTestCase, unittest.TestCase):
    from planar.c import Vec2


class VectorSeqBaseTestCase(object):

    def test_init(self):
        a = self.VecSeq([(0,1), (2,3)])
        assert_equal(tuple(a), (self.Vec2(0,1), self.Vec2(2,3)))
        a = self.VecSeq([self.Vec2(4,5)])
        assert_equal(tuple(a), (self.Vec2(4,5),))
        a = self.VecSeq([])
        assert_equal(tuple(a), ())
        a = self.VecSeq(iter(((3,4), (5,6), (7,-8))))
        assert_equal(tuple(a), 
            (self.Vec2(3,4), self.Vec2(5,6), self.Vec2(7,-8)))

    def test_from_points(self):
        a = self.VecSeq.from_points([(0,1), (2,3)])
        assert_equal(tuple(a), (self.Vec2(0,1), self.Vec2(2,3)))
        a = self.VecSeq.from_points([self.Vec2(4,5)])
        assert_equal(tuple(a), (self.Vec2(4,5),))
        a = self.VecSeq.from_points([])
        assert_equal(tuple(a), ())
        a = self.VecSeq.from_points(iter(((3,4), (5,6), (7,-8))))
        assert_equal(tuple(a), 
            (self.Vec2(3,4), self.Vec2(5,6), self.Vec2(7,-8)))

    def test_len(self):
        a = self.VecSeq([(0,1), (2,3)])
        assert_equal(len(a), 2)
        a = self.VecSeq([])
        assert_equal(len(a), 0)

    def test_bool(self):
        a = self.VecSeq([(0,1), (2,3)])
        assert a
        a = self.VecSeq([])
        assert not a

    def test_iter(self):
        i = iter(self.VecSeq([(-1,1.5), (3, 4.1)]))
        assert_equal(i.next(), self.Vec2(-1, 1.5))
        assert_equal(i.next(), self.Vec2(3, 4.1))
        self.assertRaises(StopIteration, i.next)

    def test_get_set_item(self):
        a = self.VecSeq([(0,1), (2,3)])
        a[0] = (7,8)
        assert isinstance(a[0], self.Vec2)
        assert_equal(a[0], self.Vec2(7,8))
        assert_equal(a[1], self.Vec2(2,3))
        assert_equal(a[-1], self.Vec2(2,3))
        a[-1] = self.Vec2(2.5,1)
        assert_equal(a[1], self.Vec2(2.5,1))

    @raises(IndexError)
    def test_get_bad_index(self):
        a = self.VecSeq([(1,2), (3,4), (5,6)])
        a[4]

    @raises(IndexError)
    def test_get_bad_neg_index(self):
        a = self.VecSeq([(1,2), (3,4), (5,6)])
        a[-9]

    @raises(IndexError)
    def test_set_bad_index(self):
        a = self.VecSeq([(1,2), (3,4), (5,6), (7,8)])
        a[8] = self.Vec2(3,3)

    @raises(TypeError)
    def test_get_bad_index_type(self):
        a = self.VecSeq([(0,0)])
        a['whodat']

    @raises(TypeError)
    def test_set_bad_index_type(self):
        a = self.VecSeq([(0,0)])
        a['whodat'] = self.Vec2(4,5)

    def test_imul_by_transform(self):
        b = a = self.VecSeq([(1,2), (3,4), (5,6)])
        a *= self.Affine.translation((5, -4))
        assert a is b
        V = self.Vec2
        assert_equal(tuple(a), (V(6, -2), V(8, 0), V(10, 2)))

    @raises(TypeError)
    def test_imul_incompatible(self):
        a = self.VecSeq([(1,2), (3,4)])
        a *= None

    def test_mul_by_transform(self):
        a = self.VecSeq([(1,2), (3,4), (5,6)])
        b = a * self.Affine.scale((2, -1))
        assert a is not b
        V = self.Vec2
        assert_equal(tuple(b), (V(2, -2), V(6, -4), V(10, -6)))

    @raises(TypeError)
    def test_mul_incompatible(self):
        a = self.VecSeq([(1,2), (3,4)]) * 2

    def test_eq(self):
        assert (self.VecSeq([(1,2), (3,4)]) ==
            self.VecSeq([self.Vec2(1,2), self.Vec2(3,4)]))
        assert self.VecSeq([]) == self.VecSeq([])
        assert not self.VecSeq([]) == self.VecSeq([(1,2)])
        assert not self.VecSeq([(3,4)]) == self.VecSeq([(1,2)])
        assert not self.VecSeq([(1,2), (3,4)]) == self.VecSeq([(1,2)])
        assert not self.VecSeq([(3,4)]) == [(3,4)]
        assert not self.VecSeq([(3,4)]) == None
        assert not None == self.VecSeq([(3,4)])

    def test_ne(self):
        assert self.VecSeq([]) != self.VecSeq([(1,2)])
        assert self.VecSeq([(3,4)]) != self.VecSeq([(1,2)])
        assert self.VecSeq([(1,2), (3,4)]) != self.VecSeq([(1,2)])
        assert not (self.VecSeq([(1,2), (3,4)]) !=
            self.VecSeq([self.Vec2(1,2), self.Vec2(3,4)]))
        assert not self.VecSeq([]) != self.VecSeq([])
        assert self.VecSeq([(3,4)]) != [(3,4)]
        assert self.VecSeq([(3,4)]) != None
        assert None != self.VecSeq([(3,4)])

    def test_almost_equals(self):
        from planar import EPSILON
        a = self.VecSeq([(3,2), (6,0)])
        assert a.almost_equals(a)
        b = self.VecSeq([(3 - EPSILON/2, 2), (6, EPSILON/2)])
        assert a.almost_equals(b)
        c = self.VecSeq([(3 - EPSILON/2, 2), (6, EPSILON/2), (0,0)])
        assert not a.almost_equals(c)
        assert not b.almost_equals(c)
        d = self.VecSeq([(3 - EPSILON, 2), (6, EPSILON*2)])
        assert not a.almost_equals(d)

    def test_copy(self):
        from copy import copy
        a = self.VecSeq([(2,4), (5,5), (6,7)])
        b = copy(a)
        assert a is not b
        assert isinstance(b, self.VecSeq)
        assert_equal(tuple(a), tuple(b))
        a[0] = (0, 0)
        assert_equal(b[0], self.Vec2(2, 4))
        assert_equal(tuple(copy(self.VecSeq([]))), ())

    def test_copy_subclass(self):
        from copy import copy
        class Subclass(self.VecSeq):
            pass

        a = Subclass([(0,1), (1,2)])
        b = copy(a)
        assert a is not b
        assert isinstance(b, Subclass)
        assert_equal(tuple(a), tuple(b))
        a[0] = (0, 0)
        assert_equal(b[0], self.Vec2(0, 1))

    def test_deepcopy(self):
        from copy import deepcopy
        p = self.VecSeq([(0,0), (1,0), (1,1), (0,1)])
        c = deepcopy(p)
        assert isinstance(c, self.VecSeq)
        assert c is not p
        assert_equal(tuple(c), tuple(p))
        c[0] = (0,0.1)
        assert c[0] != p[0]

    @raises(TypeError)
    def test_unhashable(self):
        hash(self.VecSeq([(3,2), (6,0)]))

    def test_subclass_with_added_init_args(self):
        class Subclass(self.VecSeq):
            def __init__(self, vectors, somearg, somekwarg=None):
                # FIXME super(Subclass, self).__init__(vectors)
                self.somearg = somearg
                self.somekwarg = somekwarg
        a = Subclass([(0,1), (1,2)], 123)
        assert isinstance(a, self.VecSeq)
        assert_equal(a.somearg, 123)
        assert_equal(a.somekwarg, None)
        b = Subclass([(0,1), (1,2)], 777, somekwarg='foo')
        assert_equal(b.somearg, 777)
        assert_equal(b.somekwarg, 'foo')


class PySeq2TestCase(VectorSeqBaseTestCase, unittest.TestCase):
    from planar.vector import Vec2
    from planar.vector import Seq2 as VecSeq
    from planar.transform import Affine


class CSeq2TestCase(VectorSeqBaseTestCase, unittest.TestCase):
    from planar.c import Vec2, Affine
    from planar.c import Seq2 as VecSeq


class Vec2ArrayBaseTestCase(object):
    
    def test_append(self):
        va = self.Vec2Array()
        assert_equal(tuple(va), ())
        va.append((3,2))
        assert_equal(tuple(va), (self.Vec2(3,2),))
        assert isinstance(va[0], self.Vec2)
        va.append(self.Vec2(4,-5))
        assert_equal(tuple(va), (self.Vec2(3,2), self.Vec2(4,-5)))
        assert isinstance(va[1], self.Vec2)

    def test_append_many(self):
        va = self.Vec2Array()
        assert_equal(tuple(va), ())
        for i in range(10000):
            va.append((-i, i))
            assert_equal(len(va), i + 1)
        for i in range(10000):
            assert_equal(va[i], self.Vec2(-i, i))

    def test_extend(self):
        va = self.Vec2Array()
        assert_equal(tuple(va), ())
        va.extend([(1,2), (3,4)])
        assert isinstance(va[0], self.Vec2)
        assert isinstance(va[1], self.Vec2)
        assert_equal(tuple(va), (self.Vec2(1,2), self.Vec2(3,4)))
        va.extend(iter([(5,6), (1,2)]))
        assert_equal(tuple(va), (self.Vec2(1,2), self.Vec2(3,4),
            self.Vec2(5,6), self.Vec2(1,2)))
        assert isinstance(va[2], self.Vec2)
        assert isinstance(va[3], self.Vec2)

    def test_insert(self):
        va = self.Vec2Array([(2,3), (9,0)])
        assert_equal(tuple(va), (self.Vec2(2,3), self.Vec2(9,0)))
        va.insert(1, (5,6))
        assert_equal(tuple(va), 
            (self.Vec2(2,3), self.Vec2(5,6), self.Vec2(9,0)))
        va.insert(0, (-1,-2))
        assert_equal(tuple(va), 
            (self.Vec2(-1,-2), self.Vec2(2,3), 
             self.Vec2(5,6), self.Vec2(9,0)))
        va.insert(100, self.Vec2(8,99))
        assert_equal(tuple(va), 
            (self.Vec2(-1,-2), self.Vec2(2,3), 
             self.Vec2(5,6), self.Vec2(9,0), self.Vec2(8,99)))

    def test_insert_many(self):
        va = self.Vec2Array()
        for i in range(10000):
            va.insert((i * 7) % (len(va) + 1), (i,-i))
            assert_equal(len(va), i + 1)

    def test_insert_neg_index(self):
        va = self.Vec2Array([(2,3), (6,7)])
        va.insert(-1, (4,5))
        assert_equal(tuple(va), 
            (self.Vec2(2,3), self.Vec2(4,5), self.Vec2(6,7)))
        va.insert(-99, (-1,-2))
        assert_equal(tuple(va), 
            (self.Vec2(-1,-2), self.Vec2(2,3), 
             self.Vec2(4,5), self.Vec2(6,7)))

    @raises(TypeError)
    def test_insert_bad_index(self):
        va = self.Vec2Array([(2,3), (9,0)])
        va.insert(None, (4,5))

    def test_delitem(self):
        va = self.Vec2Array([(2,3), (9,0)])
        assert_equal(tuple(va), (self.Vec2(2,3), self.Vec2(9,0)))
        del va[0]
        assert_equal(tuple(va), (self.Vec2(9,0),))

    def test_delitem_many(self):
        va = self.Vec2Array()
        for i in range(10000):
            va.append((i,-i))
        for i in range(10000):
            del va[(i * 7) % len(va)]
            assert_equal(len(va), 9999 - i)

    @raises(IndexError)
    def test_delitem_out_of_range(self):
        va = self.Vec2Array([(2,3), (9,0)])
        del va[2]

    @raises(TypeError)
    def test_delitem_bad_index(self):
        va = self.Vec2Array([(2,3), (9,0)])
        del va[None]

    def test_append_insert_delete_many(self):
        va = self.Vec2Array()
        for i in range(10000):
            va.append(self.Vec2(-i, -i))
            va.insert(i * 13 % len(va), self.Vec2(i, i))
            del va[(i * 3) % len(va)]
            assert_equal(len(va), i + 1)

    def test_get_front_slice(self):
        va = self.Vec2Array([(-3,0), (0,0), (2,1), (0,0.5)])
        vaslice = va[:2]
        assert isinstance(vaslice, self.Vec2Array)
        assert vaslice is not va
        assert_equal(tuple(vaslice),
            (self.Vec2(-3,0), self.Vec2(0,0)))
        vaslice = va[:-1]
        assert isinstance(vaslice, self.Vec2Array)
        assert vaslice is not va
        assert_equal(tuple(vaslice),
            (self.Vec2(-3,0), self.Vec2(0,0), self.Vec2(2,1)))

    def test_get_back_slice(self):
        va = self.Vec2Array([(-3,0), (0,0), (2,1), (0,0.5)])
        vaslice = va[2:]
        assert isinstance(vaslice, self.Vec2Array)
        assert vaslice is not va
        assert_equal(tuple(vaslice),
            (self.Vec2(2,1), self.Vec2(0,0.5)))
    
    def test_get_full_slice(self):
        va = self.Vec2Array([(-3,0), (0,0), (2,1), (0,0.5)])
        vaslice = va[:]
        assert isinstance(vaslice, self.Vec2Array)
        assert vaslice is not va
        assert_equal(tuple(vaslice), tuple(va))
    
    def test_get_mid_slice(self):
        va = self.Vec2Array([(-3,0), (0,0), (2,1), (0,0.5)])
        vaslice = va[1:3]
        assert isinstance(vaslice, self.Vec2Array)
        assert vaslice is not va
        assert_equal(tuple(vaslice), (self.Vec2(0,0), self.Vec2(2,1)))
        vaslice = va[1:-2]
        assert isinstance(vaslice, self.Vec2Array)
        assert vaslice is not va
        assert_equal(tuple(vaslice), (self.Vec2(0,0),))

    def test_get_ext_slice(self):
        va = self.Vec2Array([(-3,0), (0,0), (2,1), (0,0.5), (-1,-2)])
        vaslice = va[3:1:-1]
        assert isinstance(vaslice, self.Vec2Array)
        assert vaslice is not va
        assert_equal(tuple(vaslice), (self.Vec2(0,0.5), self.Vec2(2,1)))
        vaslice = va[:-1:2]
        assert isinstance(vaslice, self.Vec2Array)
        assert vaslice is not va
        assert_equal(tuple(vaslice), (self.Vec2(-3,0), self.Vec2(2,1)))
        vaslice = va[10::50]
        assert isinstance(vaslice, self.Vec2Array)
        assert vaslice is not va
        assert_equal(tuple(vaslice), ())

    def test_ass_slice(self):
        va = self.Vec2Array([(-3,0), (0,0), (2,1), (0,0.5)])
        va[:2] = [(1,2), (3,4)]
        assert_equal(tuple(va),
            (self.Vec2(1,2), self.Vec2(3,4), 
             self.Vec2(2,1), self.Vec2(0,0.5)))
        va[1:-2] = self.Vec2Array([(8,9), (11,10), (4,5)])
        assert_equal(tuple(va),
            (self.Vec2(1,2), self.Vec2(8,9), self.Vec2(11,10),
             self.Vec2(4,5), self.Vec2(2,1), self.Vec2(0,0.5)))
        va[1:] = self.VecSeq([(0,0)])
        assert_equal(tuple(va), (self.Vec2(1,2), self.Vec2(0,0)))

    @raises(TypeError)
    def test_ass_slice_wrong_type(self):
        va = self.Vec2Array([(-3,0), (0,0), (2,1), (0,0.5)])
        va[:2] = 3.14

    def test_ass_ext_slice(self):
        va = self.Vec2Array([(-3,0), (0,0), (2,1), (0,0.5), (-1,0), (4,4)])
        va[4:2:-1] = [(1,2), (3,4)]
        assert_equal(tuple(va),
            (self.Vec2(-3, 0), self.Vec2(0,0), self.Vec2(2,1), 
             self.Vec2(3,4), self.Vec2(1,2), self.Vec2(4,4)))
        va[::2] = self.Vec2Array([(1,1), (2,2), (3,3)])
        assert_equal(tuple(va),
            (self.Vec2(1, 1), self.Vec2(0,0), self.Vec2(2,2), 
             self.Vec2(3,4), self.Vec2(3,3), self.Vec2(4,4)))

    @raises(ValueError)
    def test_ass_ext_slice_wrong_size(self):
        va = self.Vec2Array([(-3,0), (0,0), (2,1), (0,0.5), (-1,0), (4,4)])
        va[5:2:-1] = [(1,2)]

    def test_del_slice(self):
        va = self.Vec2Array([(-3,0), (0,0), (2,1), (0,0.5)])
        del va[-1:]
        assert_equal(tuple(va),
            (self.Vec2(-3, 0), self.Vec2(0,0), self.Vec2(2,1)))
        del va[1:2]
        assert_equal(tuple(va),
            (self.Vec2(-3, 0), self.Vec2(2,1)))
        del va[1:]
        assert_equal(tuple(va), (self.Vec2(-3,0),))
        del va[:]
        assert_equal(tuple(va), ())

    def test_del_ext_slice(self):
        va = self.Vec2Array([(-3,0), (0,0), (2,1), (0,0.5), (-1,0), (4,4)])
        del va[::3]
        assert_equal(tuple(va),
            (self.Vec2(0,0), self.Vec2(2,1), 
             self.Vec2(-1,0), self.Vec2(4,4)))

    def test_longest(self):
        va = self.Vec2Array()
        assert_equal(va.longest(), None)
        va = self.Vec2Array([(2,1)])
        assert_equal(va.longest(), self.Vec2(2,1))
        va.append((-4,2))
        assert_equal(va.longest(), self.Vec2(-4,2))
        va.append((4,1.5))
        assert_equal(va.longest(), self.Vec2(-4,2))
        va.insert(1, (5,-4))
        assert_equal(va.longest(), self.Vec2(5,-4))

    def test_shortest(self):
        va = self.Vec2Array()
        assert_equal(va.shortest(), None)
        va = self.Vec2Array([(2,1)])
        assert_equal(va.shortest(), self.Vec2(2,1))
        va.append((-4,2))
        assert_equal(va.shortest(), self.Vec2(2,1))
        va.append((-1,0.75))
        assert_equal(va.shortest(), self.Vec2(-1,0.75))
        va.insert(1, (0,0))
        assert_equal(va.shortest(), self.Vec2(0,0))

    def test_normalized(self):
        va1 = self.Vec2Array()
        va2 = va1.normalized()
        assert va1 is not va2
        assert_equal(len(va2), 0)
        va1 = self.Vec2Array([(-3,0), (0,0), (2,1), (0,0.5)])
        va2 = va1.normalized()
        assert va1 is not va2
        assert_equal(tuple(va1), 
            (self.Vec2(-3,0), self.Vec2(0,0), 
             self.Vec2(2,1), self.Vec2(0,0.5)))
        assert_equal(tuple(va2), 
            (self.Vec2(-1,0), self.Vec2(0,0), 
             self.Vec2(2,1).normalized(), self.Vec2(0,1)))

    def test_normalize(self):
        va = self.Vec2Array()
        va.normalize()
        assert_equal(len(va), 0)
        va = self.Vec2Array([(-3,0), (0,0), (2,1), (0,0.5)])
        assert_equal(va.normalize(), None)
        assert_equal(tuple(va), 
            (self.Vec2(-1,0), self.Vec2(0,0), 
             self.Vec2(2,1).normalized(), self.Vec2(0,1)))

    def test_clamped(self):
        va1 = self.Vec2Array()
        va2 = va1.clamped(1, 2)
        assert va1 is not va2
        assert_equal(len(va2), 0)
        va1 = self.Vec2Array([(-3,0), (0,0), (2,1), (0,0.5)])
        va2 = va1.clamped(min_length=1)
        assert va1 is not va2
        assert_equal(tuple(va1), 
            (self.Vec2(-3,0), self.Vec2(0,0), 
             self.Vec2(2,1), self.Vec2(0,0.5)))
        assert_equal(tuple(va2), 
            (self.Vec2(-3,0), self.Vec2(0,0),
             self.Vec2(2,1), self.Vec2(0,1)))
        va2 = va1.clamped(max_length=2)
        assert_equal(tuple(va2), 
            (self.Vec2(-2,0), self.Vec2(0,0),
             self.Vec2(2,1).clamped(max_length=2), self.Vec2(0,0.5)))
        va2 = va1.clamped(min_length=1.5, max_length=2.5)
        assert_equal(tuple(va2), 
            (self.Vec2(-2.5,0), self.Vec2(0,0),
             self.Vec2(2,1), self.Vec2(0,1.5)))

    @raises(ValueError)
    def test_clamped_bad_args(self):
        va = self.Vec2Array([(3,-1)])
        va.clamped(2, 1)

    @raises(ValueError)
    def test_clamped_bad_args2(self):
        va = self.Vec2Array([(3,-1)])
        va.clamped(-1, 1)

    def test_clamp(self):
        va = self.Vec2Array()
        assert_equal(va.clamp(1, 2), None)
        assert_equal(len(va), 0)
        va = self.Vec2Array([(-3,0), (0,0), (2,1), (0,0.5)])
        va.clamp(min_length=1.25)
        assert_equal(tuple(va), 
            (self.Vec2(-3,0), self.Vec2(0,0),
             self.Vec2(2,1), self.Vec2(0,1.25)))
        va.clamp(max_length=2)
        assert_equal(tuple(va), 
            (self.Vec2(-2,0), self.Vec2(0,0),
             self.Vec2(2,1).clamped(max_length=2), self.Vec2(0,1.25)))
        va.clamp(min_length=1.5, max_length=1.75)
        assert va.almost_equals(self.Vec2Array(
            [self.Vec2(-1.75,0), self.Vec2(0,0),
            self.Vec2(2,1).clamped(max_length=1.75), self.Vec2(0,1.5)]))

    @raises(ValueError)
    def test_clamp_bad_args(self):
        va = self.Vec2Array([(3,-1)])
        va.clamp(2, 1)

    @raises(ValueError)
    def test_clamp_bad_args2(self):
        va = self.Vec2Array([(3,-1)])
        va.clamp(-1, 1)

    def test_add_arrays(self):
        va1 = self.Vec2Array([(1,2), (3,4)])
        va2 = self.Vec2Array([(-1,-1), (1,-2)])
        va3 = va1 + va2
        assert va3 is not va1
        assert va3 is not va2
        assert_equal(tuple(va3), (self.Vec2(0,1), self.Vec2(4,2)))

    def test_add_array_to_other(self):
        class Other(self.Seq2):
            pass
        va = self.Vec2Array([(0,1), (2,3), (3,4)])
        other = Other([(1,-1), (2,-2), (3,-3)])
        result = va + other
        assert result is not other
        assert isinstance(result, Other)
        assert_equal(tuple(result), 
            (self.Vec2(1,0), self.Vec2(4,1), self.Vec2(6,1)))
        result2 = other + va
        assert isinstance(result2, Other)
        assert_equal(tuple(result2), 
            (self.Vec2(1,0), self.Vec2(4,1), self.Vec2(6,1)))

    def test_add_vector_to_array(self):
        va = self.Vec2Array([(0,1), (2,3), (3,4)]) + self.Vec2(-2,3)
        assert isinstance(va, self.Vec2Array), repr(va)
        assert_equal(tuple(va),
            (self.Vec2(-2,4), self.Vec2(0,6), self.Vec2(1,7)))
        va = va + (2,-1)
        assert_equal(tuple(va),
            (self.Vec2(0,3), self.Vec2(2,5), self.Vec2(3,6)))

    @raises(ValueError)
    def test_add_arrays_of_different_length(self):
        self.Vec2Array([(0,0), (0,1)]) + self.Vec2Array([(1,2)])

    @raises(TypeError)
    def test_add_incompatible(self):
        self.Vec2Array([(0,1), (2,3), (3,4)]) + [1, 2, 3]

    def test_iadd_arrays(self):
        va = a = self.Vec2Array([(1,2), (3,4)])
        va += self.Vec2Array([(-1,-1), (1,-2)])
        assert va is a
        assert_equal(tuple(va), (self.Vec2(0,1), self.Vec2(4,2)))

    def test_iadd_array_to_other(self):
        class Other(self.Seq2):
            pass
        va = a = self.Vec2Array([(0,1), (2,3), (3,4)])
        va += Other([(1,-1), (2,-2), (3,-3)])
        assert va is a
        assert_equal(tuple(va), 
            (self.Vec2(1,0), self.Vec2(4,1), self.Vec2(6,1)))

    def test_iadd_vector_to_array(self):
        va = a = self.Vec2Array([(0,1), (2,3), (3,4)]) 
        va += self.Vec2(-2,3)
        assert va is a
        assert_equal(tuple(va),
            (self.Vec2(-2,4), self.Vec2(0,6), self.Vec2(1,7)))
        va += (-1,1)
        assert va is a
        assert_equal(tuple(va),
            (self.Vec2(-3,5), self.Vec2(-1,7), self.Vec2(0,8)))

    @raises(ValueError)
    def test_iadd_arrays_of_different_length(self):
        va = self.Vec2Array([(0,0), (0,1)]) 
        va += self.Vec2Array([(1,2), (2,2), (3,2)])

    @raises(TypeError)
    def test_iadd_incompatible(self):
        va = self.Vec2Array([(0,1), (2,3), (3,4)]) 
        va += None
        
    def test_sub_arrays(self):
        va1 = self.Vec2Array([(1,2), (3,4)])
        va2 = self.Vec2Array([(-1,-1), (1,-2)])
        va3 = va1 - va2
        assert va3 is not va1
        assert va3 is not va2
        assert_equal(tuple(va3), (self.Vec2(2,3), self.Vec2(2,6)))

    def test_sub_array_from_other(self):
        class Other(self.Seq2):
            pass
        va = self.Vec2Array([(0,1), (2,3), (3,4)])
        other = Other([(1,-1), (2,-2), (3,-3)])
        result2 = other - va
        assert isinstance(result2, Other)
        assert_equal(tuple(result2), 
            (self.Vec2(1,-2), self.Vec2(0,-5), self.Vec2(0,-7)))

    @raises(TypeError)
    def test_sub_other_from_array(self):
        class Other(self.Seq2):
            pass
        self.Vec2Array([(0,1), (2,3), (3,4)]) - Other([(1,-1), (2,-2), (3,-3)])

    def test_sub_vector_from_array(self):
        va = self.Vec2Array([(0,1), (2,3), (3,4)]) - self.Vec2(-2,3)
        assert isinstance(va, self.Vec2Array)
        assert_equal(tuple(va),
            (self.Vec2(2,-2), self.Vec2(4,0), self.Vec2(5,1)))
        va = va - (2,-1)
        assert_equal(tuple(va),
            (self.Vec2(0,-1), self.Vec2(2,1), self.Vec2(3,2)))

    @raises(TypeError)
    def test_sub_array_from_vector(self):
        self.Vec2(9, 2) - self.Vec2Array([(0,1), (2,3)])

    @raises(ValueError)
    def test_sub_arrays_of_different_length(self):
        self.Vec2Array([(0,0), (0,1)]) - self.Vec2Array([(1,2)])

    @raises(ValueError)
    def test_rsub_arrays_of_different_length(self):
        class Other(self.Seq2):
            pass
        Other([(0,0), (0,1)]) - self.Vec2Array([(1,2)])

    @raises(TypeError)
    def test_sub_incompatible(self):
        self.Vec2Array([(0,1), (2,3), (3,4)]) - [1, 2, 3]

    @raises(TypeError)
    def test_rsub_incompatible(self):
        None - self.Vec2Array([(0,1), (2,3), (3,4)])

    def test_isub_arrays(self):
        va = a = self.Vec2Array([(1,2), (3,4)])
        va -= self.Vec2Array([(-1,-1), (1,-2)])
        assert va is a
        assert_equal(tuple(va), (self.Vec2(2,3), self.Vec2(2,6)))

    @raises(TypeError)
    def test_isub_other_from_array(self):
        class Other(self.Seq2):
            pass
        va = self.Vec2Array([(0,1), (2,3), (3,4)])
        va -= Other([(1,-1), (2,-2), (3,-3)])

    def test_isub_vector_from_array(self):
        va = a = self.Vec2Array([(0,1), (2,3), (3,4)]) 
        va -= self.Vec2(-2,3)
        assert va is a
        assert_equal(tuple(va),
            (self.Vec2(2,-2), self.Vec2(4,0), self.Vec2(5,1)))
        va -= (-1,1)
        assert va is a
        assert_equal(tuple(va),
            (self.Vec2(3,-3), self.Vec2(5,-1), self.Vec2(6,0)))

    @raises(ValueError)
    def test_isub_arrays_of_different_length(self):
        va = self.Vec2Array([(0,0), (0,1)]) 
        va -= self.Vec2Array([(1,2), (2,2), (3,2)])

    @raises(TypeError)
    def test_isub_incompatible(self):
        va = self.Vec2Array([(0,1), (2,3), (3,4)]) 
        va -= None
        
    def test_mul_arrays(self):
        va1 = self.Vec2Array([(1,2), (3,4)])
        va2 = self.Vec2Array([(-1,-1), (1,-2)])
        va3 = va1 * va2
        assert va3 is not va1
        assert va3 is not va2
        assert_equal(tuple(va3), (self.Vec2(-1,-2), self.Vec2(3,-8)))

    def test_mul_array_with_other(self):
        class Other(self.Seq2):
            pass
        va = self.Vec2Array([(0,1), (2,3), (3,4)])
        other = Other([(1,-1), (2,-2), (3,-3)])
        result = va * other
        assert result is not other
        assert isinstance(result, Other)
        assert_equal(tuple(result), 
            (self.Vec2(0,-1), self.Vec2(4,-6), self.Vec2(9,-12)))
        result2 = other * va
        assert isinstance(result2, Other)
        assert_equal(tuple(result2), 
            (self.Vec2(0,-1), self.Vec2(4,-6), self.Vec2(9,-12)))

    def test_mul_vector_with_array(self):
        va = self.Vec2Array([(0,1), (2,3), (3,4)]) * self.Vec2(-2,3)
        assert isinstance(va, self.Vec2Array)
        assert_equal(tuple(va),
            (self.Vec2(0,3), self.Vec2(-4,9), self.Vec2(-6,12)))
        va = self.Vec2(-2,3) * self.Vec2Array([(0,1), (2,3), (3,4)])
        assert isinstance(va, self.Vec2Array)
        assert_equal(tuple(va),
            (self.Vec2(0,3), self.Vec2(-4,9), self.Vec2(-6,12)))
        # XXX doesn't work in py3
        # va = va * (2,-1)
        # assert_equal(tuple(va),
        #    (self.Vec2(0,-3), self.Vec2(-8,-9), self.Vec2(-12,-12)))

    def test_mul_vector_with_scalar(self):
        va = self.Vec2Array([(0,1), (2,3), (3,4)]) * 4
        assert isinstance(va, self.Vec2Array)
        assert_equal(tuple(va),
            (self.Vec2(0,4), self.Vec2(8,12), self.Vec2(12, 16)))
        va = 4 * self.Vec2Array([(0,1), (2,3), (3,4)])
        assert isinstance(va, self.Vec2Array)
        assert_equal(tuple(va),
            (self.Vec2(0,4), self.Vec2(8,12), self.Vec2(12, 16)))

    @raises(ValueError)
    def test_mul_arrays_of_different_length(self):
        self.Vec2Array([(0,0), (0,1)]) * self.Vec2Array([(1,2)])

    @raises(TypeError)
    def test_mul_incompatible(self):
        self.Vec2Array([(0,1), (2,3), (3,4)]) * [1, 2, 3]

    def test_imul_arrays(self):
        va = a = self.Vec2Array([(1,2), (3,4)])
        va *= self.Vec2Array([(-1,-1), (1,-2)])
        assert va is a
        assert_equal(tuple(va), (self.Vec2(-1,-2), self.Vec2(3,-8)))

    @raises(TypeError)
    def test_imul_array_with_other(self):
        class Other(self.Seq2):
            pass
        va = self.Vec2Array([(0,1), (2,3), (3,4)])
        va *= Other([(1,-1), (2,-2), (3,-3)])

    def test_imul_vector_with_array(self):
        va = a = self.Vec2Array([(0,1), (2,3), (3,4)]) 
        va *= self.Vec2(-2,3)
        assert va is a
        assert_equal(tuple(va),
            (self.Vec2(0,3), self.Vec2(-4,9), self.Vec2(-6,12)))

    def test_imul_vector_with_scalar(self):
        va = a = self.Vec2Array([(0,1), (2,3), (3,4)]) 
        va *= 4
        assert va is a
        assert_equal(tuple(va),
            (self.Vec2(0,4), self.Vec2(8,12), self.Vec2(12, 16)))

    @raises(ValueError)
    def test_imul_arrays_of_different_length(self):
        va = self.Vec2Array([(0,0), (0,1)]) 
        va *= self.Vec2Array([(1,2)])

    @raises(TypeError)
    def test_imul_incompatible(self):
        va = self.Vec2Array([(0,1), (2,3), (3,4)]) 
        va *= [1, 2, 3]

    def test_truediv_arrays(self):
        va1 = self.Vec2Array([(1,2), (3,5)])
        va2 = self.Vec2Array([(-1,-1), (1,-2)])
        va3 = va1 / va2
        assert va3 is not va1
        assert va3 is not va2
        assert_equal(tuple(va3), (self.Vec2(-1,-2), self.Vec2(3,-2.5)))

    def test_truediv_other_by_array(self):
        class Other(self.Seq2):
            pass
        va = self.Vec2Array([(2,1), (2,3), (3,4)])
        other = Other([(1,-1), (2,-2), (3,-3)])
        result = other / va
        assert isinstance(result, Other)
        assert_equal(tuple(result), 
            (self.Vec2(0.5,-1), self.Vec2(1,-2/3), self.Vec2(1,-0.75)))

    def test_truediv_array_by_vector(self):
        va = self.Vec2Array([(2,1), (1,3), (3,4)]) / self.Vec2(-2,3)
        assert isinstance(va, self.Vec2Array)
        assert_equal(tuple(va),
            (self.Vec2(-1,1/3), self.Vec2(-0.5,1), self.Vec2(-1.5,4/3)))

    @raises(TypeError)
    def test_truediv_vector_by_array(self):
        self.Vec2(-2,3) / self.Vec2Array([(0,1), (2,3), (3,4)])

    def test_truediv_vector_with_scalar(self):
        va = self.Vec2Array([(0,1), (5,3), (3,4)]) / 4
        assert isinstance(va, self.Vec2Array)
        assert_equal(tuple(va),
            (self.Vec2(0,0.25), self.Vec2(1.25,0.75), self.Vec2(0.75, 1)))

    @raises(ValueError)
    def test_rtruediv_arrays_of_different_length(self):
        class Other(self.Seq2):
            pass
        Other([(1,2)]) / self.Vec2Array([(0,0), (0,1)])
        
    @raises(ValueError)
    def test_truediv_arrays_of_different_length(self):
        self.Vec2Array([(0,0), (0,1)]) / self.Vec2Array([(1,2)])

    @raises(TypeError)
    def test_truediv_incompatible(self):
        self.Vec2Array([(0,1), (2,3), (3,4)]) / [1, 2, 3]

    @raises(ZeroDivisionError)
    def test_truediv_by_zero_scalar(self):
        self.Vec2Array([(0,1), (2,3), (3,4)]) / 0

    @raises(ZeroDivisionError)
    def test_truediv_by_zero_vector(self):
        self.Vec2Array([(0,1), (2,3), (3,4)]) / self.Vec2(-1,0)

    @raises(ZeroDivisionError)
    def test_truediv_by_zero_vector_array(self):
        self.Vec2Array([(0,1), (2,3)]) / self.Vec2Array([(1,1), (0,3)]) 

    def test_itruediv_arrays(self):
        va = a = self.Vec2Array([(1,2), (3,4)])
        va /= self.Vec2Array([(-1,-5), (1,-3)])
        assert va is a
        assert_equal(tuple(va), (self.Vec2(-1,-2/5), self.Vec2(3,-4/3)))

    def test_itruediv_other_by_array(self):
        class Other(self.Seq2):
            pass
        other = Other([(1,-1), (2,-2), (3,-3)])
        other /= self.Vec2Array([(3,1), (2,3), (3,4)])
        assert isinstance(other, Other)
        assert_equal(tuple(other),
            (self.Vec2(1/3, -1), self.Vec2(1,-2/3), self.Vec2(1,-0.75)))

    @raises(TypeError)
    def test_itruediv_array_by_other(self):
        class Other(self.Seq2):
            pass
        va = self.Vec2Array([(0,1), (2,3), (3,4)])
        va /= Other([(1,-1), (2,-2), (3,-3)])

    def test_itruediv_array_by_vector(self):
        va = a = self.Vec2Array([(0,1), (2,3), (3,4)]) 
        va /= self.Vec2(-2,3)
        assert va is a
        assert_equal(tuple(va),
            (self.Vec2(0,1/3), self.Vec2(-1,1), self.Vec2(-1.5,4/3)))

    def test_itruediv_vector_with_scalar(self):
        va = a = self.Vec2Array([(0,1), (2,3), (3,4)]) 
        va /= 4
        assert va is a
        assert_equal(tuple(va),
            (self.Vec2(0,0.25), self.Vec2(0.5,0.75), self.Vec2(0.75, 1)))

    @raises(ValueError)
    def test_itruediv_arrays_of_different_length(self):
        va = self.Vec2Array([(0,0), (0,1)]) 
        va /= self.Vec2Array([(1,2)])

    @raises(TypeError)
    def test_itruediv_incompatible(self):
        va = self.Vec2Array([(0,1), (2,3), (3,4)]) 
        va /= [1, 2, 3]

    @raises(ZeroDivisionError)
    def test_itruediv_by_zero_scalar(self):
        va = self.Vec2Array([(0,1), (2,3), (3,4)]) 
        va /= 0

    @raises(ZeroDivisionError)
    def test_itruediv_by_zero_vector(self):
        va = self.Vec2Array([(0,1), (2,3), (3,4)]) 
        va /= self.Vec2(-1,0)

    @raises(ZeroDivisionError)
    def test_itruediv_by_zero_vector_array(self):
        va = self.Vec2Array([(0,1), (2,3)]) 
        va /= self.Vec2Array([(1,1), (0,3)]) 

    def test_floordiv_arrays(self):
        va1 = self.Vec2Array([(1,2), (3,5)])
        va2 = self.Vec2Array([(-1,-1), (1,-2)])
        va3 = va1 // va2
        assert va3 is not va1
        assert va3 is not va2
        assert_equal(tuple(va3), (self.Vec2(-1,-2), self.Vec2(3,-3)))

    def test_floordiv_other_by_array(self):
        class Other(self.Seq2):
            pass
        va = self.Vec2Array([(2,1), (2,3), (3,4)])
        other = Other([(1,-1), (2,-2), (3,-3)])
        result = other // va
        assert isinstance(result, Other)
        assert_equal(tuple(result), 
            (self.Vec2(0,-1), self.Vec2(1,-1), self.Vec2(1,-1)))

    def test_floordiv_array_by_vector(self):
        va = self.Vec2Array([(2,1), (1,3), (3,4)]) // self.Vec2(-2,3)
        assert isinstance(va, self.Vec2Array)
        assert_equal(tuple(va),
            (self.Vec2(-1,0), self.Vec2(-1,1), self.Vec2(-2,1)))

    @raises(TypeError)
    def test_floordiv_vector_by_array(self):
        self.Vec2(-2,3) // self.Vec2Array([(0,1), (2,3), (3,4)])

    def test_floordiv_vector_with_scalar(self):
        va = self.Vec2Array([(0,1), (5,3), (3,4)]) // 4
        assert isinstance(va, self.Vec2Array)
        assert_equal(tuple(va),
            (self.Vec2(0,0), self.Vec2(1,0), self.Vec2(0, 1)))

    @raises(ValueError)
    def test_floordiv_arrays_of_different_length(self):
        self.Vec2Array([(0,0), (0,1)]) // self.Vec2Array([(1,2)])

    @raises(ValueError)
    def test_rfloordiv_arrays_of_different_length(self):
        class Other(self.Seq2):
            pass
        Other([(1,2)]) // self.Vec2Array([(0,0), (0,1)])

    @raises(TypeError)
    def test_floordiv_incompatible(self):
        self.Vec2Array([(0,1), (2,3), (3,4)]) // [1, 2, 3]

    @raises(ZeroDivisionError)
    def test_floordiv_by_zero_scalar(self):
        self.Vec2Array([(0,1), (2,3), (3,4)]) // 0

    @raises(ZeroDivisionError)
    def test_floordiv_by_zero_vector(self):
        self.Vec2Array([(0,1), (2,3), (3,4)]) // self.Vec2(-1,0)

    @raises(ZeroDivisionError)
    def test_floordiv_by_zero_vector_array(self):
        self.Vec2Array([(0,1), (2,3)]) // self.Vec2Array([(1,1), (0,3)]) 

    def test_ifloordiv_arrays(self):
        va = a = self.Vec2Array([(1,2), (3,4)])
        va //= self.Vec2Array([(-1,-5), (1,-3)])
        assert va is a
        assert_equal(tuple(va), (self.Vec2(-1,-1), self.Vec2(3,-2)))

    def test_ifloordiv_other_by_array(self):
        class Other(self.Seq2):
            pass
        other = Other([(1,-1), (2,-2), (3,-9)])
        other //= self.Vec2Array([(3,1), (2,3), (3,4)])
        assert isinstance(other, Other)
        assert_equal(tuple(other),
            (self.Vec2(0, -1), self.Vec2(1,-1), self.Vec2(1,-3)))

    @raises(TypeError)
    def test_ifloordiv_array_by_other(self):
        class Other(self.Seq2):
            pass
        va = self.Vec2Array([(0,1), (2,3), (3,4)])
        va //= Other([(1,-1), (2,-2), (3,-3)])

    def test_ifloordiv_array_by_vector(self):
        va = a = self.Vec2Array([(0,1), (2,3), (3,7)]) 
        va //= self.Vec2(-2,3)
        assert va is a
        assert_equal(tuple(va),
            (self.Vec2(0,0), self.Vec2(-1,1), self.Vec2(-2,2)))

    def test_ifloordiv_vector_with_scalar(self):
        va = a = self.Vec2Array([(0,1), (2,4), (3,9)]) 
        va //= 4
        assert va is a
        assert_equal(tuple(va),
            (self.Vec2(0,0), self.Vec2(0,1), self.Vec2(0,2)))

    @raises(ValueError)
    def test_ifloordiv_arrays_of_different_length(self):
        va = self.Vec2Array([(0,0), (0,1)]) 
        va //= self.Vec2Array([(1,2)])

    @raises(TypeError)
    def test_ifloordiv_incompatible(self):
        va = self.Vec2Array([(0,1), (2,3), (3,4)]) 
        va //= [1, 2, 3]

    @raises(ZeroDivisionError)
    def test_ifloordiv_by_zero_scalar(self):
        va = self.Vec2Array([(0,1), (2,3), (3,4)]) 
        va //= 0

    @raises(ZeroDivisionError)
    def test_ifloordiv_by_zero_vector(self):
        va = self.Vec2Array([(0,1), (2,3), (3,4)]) 
        va //= self.Vec2(-1,0)

    @raises(ZeroDivisionError)
    def test_ifloordiv_by_zero_vector_array(self):
        va = self.Vec2Array([(0,1), (2,3)]) 
        va //= self.Vec2Array([(1,1), (0,3)])

    def test_neg(self):
        a = self.Vec2Array([(0,1), (2,3), (3,4)])
        na = -a
        assert na is not a
        assert_equal(tuple(na),
            (self.Vec2(0,-1), self.Vec2(-2,-3), self.Vec2(-3,-4)))
        assert_equal(tuple(a),
            (self.Vec2(0,1), self.Vec2(2,3), self.Vec2(3,4)))

    def test_pos(self):
        a = self.Vec2Array([(0,1), (2,3), (3,4)])
        pa = +a
        assert pa is not a
        assert_equal(tuple(pa),
            (self.Vec2(0,1), self.Vec2(2,3), self.Vec2(3,4)))

    def test_bool(self):
        assert self.Vec2Array([(0,1), (2,3)])
        assert not self.Vec2Array()

    def test_repr_and_str(self):
        va = self.Vec2Array([(0,1.5), (2,3)])
        assert_equal(repr(va), 'Vec2Array([(0.0, 1.5), (2.0, 3.0)])')
        assert_equal(repr(va), str(va))


class PyVec2ArrayTestCase(
    Vec2ArrayBaseTestCase, VectorSeqBaseTestCase, unittest.TestCase):
    from planar.vector import Vec2Array
    from planar.vector import Vec2Array as VecSeq
    from planar.vector import Vec2, Seq2
    from planar.transform import Affine


class CVec2ArrayTestCase(
    Vec2ArrayBaseTestCase, VectorSeqBaseTestCase, unittest.TestCase):
    from planar.c import Vec2Array
    from planar.c import Vec2Array as VecSeq
    from planar.c import Vec2, Seq2, Affine

    def test_repr_and_str(self):
        va = self.Vec2Array([(0,1.5), (2,3)])
        assert_equal(repr(va), 'Vec2Array([(0, 1.5), (2, 3)])')
        assert_equal(repr(va), str(va))


if __name__ == '__main__':
    unittest.main()


# vim: ai ts=4 sts=4 et sw=4 tw=78

