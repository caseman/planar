"""Vector class unit tests"""

from __future__ import division
import sys
import math
import unittest
from nose.tools import assert_equal, assert_almost_equal, raises


class Vec2BaseTestCase:

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
        assert_almost_equal(v2.angle, -90)
        assert_almost_equal(v2.x, 0)
        assert_almost_equal(v2.y, -10)

        assert_equal(self.Vec2.polar(10, 10), 
            self.Vec2.polar(angle=10, length=10))

        assert_almost_equal(self.Vec2.polar(361).angle, 1)

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

    def test_sub(self):
        assert_equal(self.Vec2(3, 3) - self.Vec2(1, 4), self.Vec2(2, -1))
        v = self.Vec2(-1, 3)
        v -= self.Vec2(3, 3)
        assert_equal(v, self.Vec2(-4, 0))

    def test_mul(self):
        assert_equal(self.Vec2(2, 3) * 2, self.Vec2(4, 6))
        assert_equal(3 * self.Vec2(2, 1), self.Vec2(6, 3))
        assert_equal(self.Vec2(5, 2) * self.Vec2(0, -1), self.Vec2(0, -2))
        v = self.Vec2(3, 2)
        v *= 4
        assert_equal(v, self.Vec2(12, 8))
        v *= self.Vec2(-1, 2)
        assert_equal(v, self.Vec2(-12, 16))

    def test_truediv(self):
        assert_equal(self.Vec2(1, 4) / 2, self.Vec2(0.5, 2))
        assert_equal(6 / self.Vec2(1, 4), self.Vec2(6, 1.5))
        assert_equal(self.Vec2(1, 4) / self.Vec2(4, 2), self.Vec2(0.25, 2))
        assert_equal(self.Vec2(1, 4) / (4, 2), self.Vec2(0.25, 2))
        assert_equal((1, 4) / self.Vec2(4, 2), self.Vec2(0.25, 2))
        v = self.Vec2(6, 3)
        v /= 3
        assert_equal(v, self.Vec2(2, 1))

    def test_floordiv(self):
        assert_equal(self.Vec2(1, 4) // 2, self.Vec2(0, 2))
        assert_equal(5 // self.Vec2(2, 4), self.Vec2(2, 1))
        assert_equal(self.Vec2(1, 4) // self.Vec2(4, 2), self.Vec2(0, 2))
        assert_equal(self.Vec2(1, 4) // (4, 2), self.Vec2(0, 2))
        assert_equal((1, 4) // self.Vec2(4, 2), self.Vec2(0, 2))
        v = self.Vec2(6, 2)
        v //= 3
        assert_equal(v, self.Vec2(2, 0))

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
    from planar.cvector import Vec2


if __name__ == '__main__':
    unittest.main()


# vim: ai ts=4 sts=4 et sw=4 tw=78
