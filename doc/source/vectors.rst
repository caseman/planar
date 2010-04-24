Vector Objects
==============

.. currentmodule:: planar

Vectors are the foundational ``planar`` objects. They are used to
represent 2D vectors and geometric points. 

:class:`planar.Vec2` objects are two dimensional, double precision
floating-point vectors. They can be initialized from either cartesian
or polar coordinates::

	>>> from planar import Vec2
	>>> v = Vec2(0, 1)
	>>> v.x
	0.0
	>>> v.y
	1.0
	>>> p = Vec2.polar(angle=45, length=10)
	>>> p.angle
	45.0
	>>> p.length
	10.0
	>>> p
	Vec2(7.0710678118654755, 7.071067811865475)

.. note:: All angles in planar are represented in degrees
	where ``0`` is parallel to the ascending x-axis, and
	``90`` is parallel to the ascending y-axis.

Internally, vectors are represented as cartesian coordinates, which
are accessible via their ``x`` and ``y`` attributes, as above, or as
a sequence with length 2::

	>>> from planar import Vec2
	>>> v = Vec2(13, 42)
	>>> len(v)
	2
	>>> v[0]
	13.0
	>>> v[1]
	42.0
	>>> x, y = v

Regardless of how the vector is created, you can always access it
in terms of polar or cartesian coordinates::

	>>> from planar import Vec2
	>>> v = Vec2(0, 5)
	>>> v.angle
	90.0
	>>> v.length
	5.0

If you omit the ``length`` parameter when using the :meth:`polar`
method, you get a unit vector in the specified direction. This
is also a handy way to compute the sine and cosine of an angle
in a single call::

	>>> import math
	>>> from planar import Vec2
	>>> cosine, sine = Vec2.polar(60)
	>>> assert cosine == math.cos(math.radians(60))
	>>> assert sine == math.sin(math.radians(60))

Vector objects are immutable, like tuples or complex numbers.  To modify a
vector, you can perform arithmetic on it. This always generates a new vector
object::

	>>> from planar import Vec2
	>>> Vec2(2, 1) + Vec2(3, 5)
	Vec2(5.0, 6.0)
	>>> Vec2(1, 0) - Vec2(1, 1)
	Vec2(0.0, -1.0)

You can multiply or divide a vector by a scalar to scale it::
	
	>>> from planar import Vec2
	>>> Vec2(1.5, 4) * 2
	Vec2(3.0, 8.0)
	>>> Vec2(9, 3) / 3
	Vec2(3.0, 1.0)

You can multiply a vector by another vector to scale it
component-wise. This skews the vector::

	>>> from planar import Vec2
	>>> Vec2(2, 3) * Vec2(5, 3)
	Vec2(10.0, 9.0)

There are special methods for performing the dot product
and cross products of two vectors explicitly. These return
scalar values:

>>> from planar import Vec2
>>> Vec2(4, 4).dot(Vec2(-4, 4)) # perpendicular
0.0

Vectors can be compared to each other or directly to
two element number sequences, such as tuples and lists.
A vector is considered "greater" than another vector
if it has a larger length::

	>>> from planar import Vec2
	>>> Vec2(0, 0) == (0, 0)
	True
	>>> Vec2(10, 1) > Vec2(-5, 5)
	True
	>>> Vec2(1, 1) <= Vec2(1, -1)
	True

Since vectors are immutable, they can be members of sets
or used as dictionary keys::

	>>> from planar import Vec2
	>>> s = set([Vec2(1, 1), Vec2(-1, 1), Vec2(-1, -1), Vec2(1, -2)])
	>>> Vec2(-1, 1) in s
	True
	>>> Vec2(0, 1) in s
	False

Vectors support many other operations in addition to the above. See the
:class:`planar.Vec2` class reference for complete details.

