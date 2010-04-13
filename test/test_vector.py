from __future__ import division
import math
from nose.tools import assert_equal, assert_almost_equal, raises

@raises(TypeError)
def test_too_few_args_zero():
    from planar import Vec2
    Vec2()

@raises(TypeError)
def test_too_few_args_one():
    from planar import Vec2
    Vec2(42)

@raises(TypeError)
def test_too_many_args():
    from planar import Vec2
    Vec2(1, 2, 3, 4)

@raises(TypeError)
def test_wrong_arg_type():
    from planar import Vec2
    Vec2('2', 'arg')

def test_polar():
    from planar import Vec2
    v = Vec2.polar(60)
    assert isinstance(v, Vec2)
    assert_almost_equal(v.angle, 60)
    assert_almost_equal(v.length, 1.0)
    assert_almost_equal(v.x, math.cos(math.radians(60)))
    assert_almost_equal(v.y, math.sin(math.radians(60)))
    
    v2 = Vec2.polar(-90, 10)
    assert_almost_equal(v2.length, 10)
    assert_almost_equal(v2.angle, -90)
    assert_almost_equal(v2.x, 0)
    assert_almost_equal(v2.y, -10)

    assert_almost_equal(Vec2.polar(361).angle, 1)

@raises(TypeError)
def test_polar_bad_angle():
    from planar import Vec2
    Vec2.polar('44')

@raises(TypeError)
def test_polar_bad_length():
    from planar import Vec2
    Vec2.polar(0, 'yikes')

def test_members_are_floats():
    from planar import Vec2
    x, y = Vec2(1, 5)
    assert isinstance(x, float)
    assert isinstance(y, float)

@raises(TypeError)
def test_immutable_members():
    from planar import Vec2
    v = Vec2(1, 1)
    v[0] = 0

def test_len():
    from planar import Vec2
    assert_equal(len(Vec2(1, 1)), 2)

def test_str():
    from planar import Vec2
    assert_equal(str(Vec2(-3.5, 4.446)), 'Vec2(-3.50, 4.45)')

def test_repr():
    from planar import Vec2
    assert_equal(repr(Vec2(-3.5, 4.446)), 'Vec2(-3.5, 4.4459999999999997)')

def test_coords():
    from planar import Vec2
    v = Vec2(1, 3)
    assert v.x == v[0] == 1
    assert v.y == v[1] == 3

@raises(AttributeError)
def test_immutable_x():
    from planar import Vec2
    v = Vec2(1, 3)
    v.x = 4
    
@raises(AttributeError)
def test_immutable_y():
    from planar import Vec2
    v = Vec2(1, 3)
    v.y = -2

def test_length2():
    from planar import Vec2
    v = Vec2(2, 3)
    assert_equal(v.length2, 13)
    # do the assert again to test the cache
    assert_equal(v.length2, 13)

def test_length():
    from planar import Vec2
    v = Vec2(3, 4)
    assert_equal(v.length, 5)
    # do the assert again to test the cache
    assert_equal(v.length, 5)

def test_is_null():
    from planar import Vec2, EPSILON
    assert Vec2(0, 0).is_null
    assert Vec2(EPSILON / 2, -EPSILON / 2).is_null
    assert not Vec2(EPSILON, 0).is_null
    assert not Vec2(1, 0).is_null
    assert not Vec2(0, -0.1).is_null
    assert not Vec2(float('nan'), 0).is_null

def test_almost_equals():
    from planar import Vec2, EPSILON
    v = Vec2(-1, 56)
    assert v.almost_equals(v)
    assert v.almost_equals(Vec2(-1 + EPSILON/2, 56))
    assert v.almost_equals(Vec2(-1 - EPSILON/2, 56))
    assert v.almost_equals(Vec2(-1, 56 - EPSILON/2))
    assert not v.almost_equals(Vec2(-1 - EPSILON, 56))
    assert not v.almost_equals(Vec2(-1, 56 + EPSILON))
    assert not v.almost_equals(Vec2(1, 56))

def test_angle():
    from planar import Vec2
    assert_equal(Vec2(1,0).angle, 0)
    assert_equal(Vec2(0,1).angle, 90)
    assert_equal(Vec2(1,1).angle, 45)
    assert_equal(Vec2(-1,0).angle, 180)
    assert_equal(Vec2(0,-1).angle, -90)
    assert_equal(Vec2(-1,-1).angle, -135)

def test_angle_to():
    from planar import Vec2
    assert_almost_equal(Vec2(1,1).angle_to(Vec2(1,1)), 0)
    assert_almost_equal(Vec2(1,1).angle_to(Vec2(0,1)), 45)
    assert_almost_equal(Vec2(1,1).angle_to(Vec2(1,0)), -45)
    assert_almost_equal(Vec2(1,0).angle_to(Vec2(1,1)), 45)
    assert_almost_equal(Vec2(1,-1).angle_to(Vec2(1,1)), 90)
    assert_almost_equal(Vec2(1,1).angle_to(Vec2(-1,-1)), -180)

def test_normalized():
    from planar import Vec2
    n = Vec2(1,1).normalized()
    assert_almost_equal(n.length, 1)
    assert_almost_equal(n.x, 1 / math.sqrt(2))
    assert_almost_equal(n.y, 1 / math.sqrt(2))

    n = Vec2(10, 0).normalized()
    assert_almost_equal(n.length, 1)
    assert_almost_equal(n.x, 1)
    assert_almost_equal(n.y, 0)

def test_safe_normalized():
    from planar import Vec2
    n = Vec2(1,1).safe_normalized()
    assert_almost_equal(n.length, 1)
    assert_almost_equal(n.x, 1 / math.sqrt(2))
    assert_almost_equal(n.y, 1 / math.sqrt(2))

    assert_equal(Vec2(0, 0).safe_normalized(), Vec2(0, 0))

def test_perpendicular():
    from planar import Vec2
    assert_equal(Vec2(10,0).perpendicular(), Vec2(0, 10))
    assert_equal(Vec2(2,2).perpendicular(), Vec2(-2, 2))

def test_dot():
    from planar import Vec2
    v1 = Vec2.polar(60, 5)
    v2 = Vec2.polar(80, 7)
    assert_almost_equal(v1.dot(v2), 5 * 7 * math.cos(math.radians(20)))

def test_cross():
    from planar import Vec2
    v1 = Vec2.polar(10, 4)
    v2 = Vec2.polar(35, 6)
    assert_almost_equal(v1.cross(v2), 4 * 6 * math.sin(math.radians(25)))

def test_distance_to():
    from planar import Vec2
    assert_equal(Vec2(3,0).distance_to(Vec2(0,4)), 5)

def test_comparison():
    from planar import Vec2
    v1 = Vec2(1, 2)
    v2 = Vec2(2, 3)
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

def test_add():
    from planar import Vec2
    assert_equal(Vec2(1, 2) + Vec2(3, 4), Vec2(4, 6))
    v = Vec2(2, 2)
    v += Vec2(1, 0)
    assert_equal(v, Vec2(3, 2))

def test_sub():
    from planar import Vec2
    assert_equal(Vec2(3, 3) - Vec2(1, 4), Vec2(2, -1))
    v = Vec2(-1, 3)
    v -= Vec2(3, 3)
    assert_equal(v, Vec2(-4, 0))

def test_mul():
    from planar import Vec2
    assert_equal(Vec2(2, 3) * 2, Vec2(4, 6))
    assert_equal(3 * Vec2(2, 1), Vec2(6, 3))
    assert_equal(Vec2(5, 2) * Vec2(0, -1), Vec2(0, -2))
    v = Vec2(3, 2)
    v *= 4
    assert_equal(v, Vec2(12, 8))
    v *= Vec2(-1, 2)
    assert_equal(v, Vec2(-12, 16))

def test_truediv():
    from planar import Vec2
    assert_equal(Vec2(1, 4) / 2, Vec2(0.5, 2))
    assert_equal(Vec2(1, 4) / Vec2(4, 2), Vec2(0.25, 2))
    v = Vec2(6, 3)
    v /= 3
    assert_equal(v, Vec2(2, 1))

def test_floordiv():
    from planar import Vec2
    assert_equal(Vec2(1, 4) // 2, Vec2(0, 2))
    assert_equal(Vec2(1, 4) // Vec2(4, 2), Vec2(0, 2))
    v = Vec2(6, 2)
    v //= 3
    assert_equal(v, Vec2(2, 0))

def test_neg():
    from planar import Vec2
    assert_equal(-Vec2(5,6), Vec2(-5,-6))

