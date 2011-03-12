from nose.tools import assert_equal, assert_almost_equal, raises

def test_version_info():
    import planar
    assert_equal('%s.%s.%s' % planar.__versioninfo__, planar.__version__)

def test_default_implementation():
    import planar
    import planar.c
    assert_equal(planar.__implementation__, 'C')
    assert planar.Vec2 is planar.c.Vec2, planar.Vec2

def test_default_epsilon():
    import planar
    assert_equal(planar.EPSILON, 1e-5)
    assert_equal(planar.EPSILON2, 1e-5**2)

def test_set_epsilon():
    import planar
    old_e = planar.EPSILON
    assert not planar.Vec2(0,0).almost_equals((0.01, 0))
    try:
        planar.set_epsilon(0.02)
        assert_equal(planar.EPSILON, 0.02)
        assert_equal(planar.EPSILON2, 0.0004)
        assert planar.Vec2(0,0).almost_equals((0.01, 0))
    finally:
        planar.set_epsilon(old_e)
    assert_equal(planar.EPSILON, old_e)
    assert_equal(planar.EPSILON2, old_e**2)
    assert not planar.Vec2(0,0).almost_equals((0.01, 0))

def test_py_imports():
	import planar
	import planar.py
	from planar.py import (Vec2, Point, Vec2Array, Seq2, 
		Line, Ray, LineSegment, Affine, BoundingBox, Polygon)
	assert set(planar.py.__all__).issubset(set(planar.__all__)), (
		planar.py.__all__, planar.__all__)

def test_c_imports():
	import planar.c
	from planar.c import (Vec2, Vec2Array, Seq2, 
		Affine, BoundingBox, Polygon)

def test_direct_imports():
	from planar import (Vec2, Point, Vec2Array, Seq2, 
		Affine, BoundingBox, Polygon)

