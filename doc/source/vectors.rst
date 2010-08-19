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
	Vec2(7.07107, 7.07107)

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
	Vec2(5, 6)
	>>> Vec2(1, 0) - Vec2(1, 1)
	Vec2(0, -1)

You can multiply or divide a vector by a scalar to scale it::
	
	>>> from planar import Vec2
	>>> Vec2(1.5, 4) * 2
	Vec2(3, 8)
	>>> Vec2(9, 3) / 3
	Vec2(3, 1)

You can multiply a vector by another vector to scale it
component-wise. This skews the vector::

	>>> from planar import Vec2
	>>> Vec2(2, 3) * Vec2(5, 3)
	Vec2(10, 9)

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

Vector Sequences
----------------

Planar provides two classes for working efficiently with batches of vectors:
:class:`~planar.Seq2` and :class:`~planar.Vec2Array`.

:class:`~planar.Seq2` is a mutable, but fixed-length, sequence of vectors.  It
is intended to be used as a base-class for objects and shapes that consist of
multiple vectors or points. Although you can instantiate :class:`~planar.Seq2`
objects, there is probably no real reason to do so. Its main use is as a base
class that provides efficient vector storage.  :class:`~planar.Seq2` has no
built-in functionality other than the basic Python sequence API.

:class:`~planar.Vec2Array` is a full-featured vector sequence which provides
efficient storage and batch-operations for arbitrarily large collections of
:class:`~planar.Vec2` objects. It is a subclass of :class:`~planar.Seq2`.
From the application's point of view, a :class:`~planar.Vec2Array` looks and
behaves just like a Python list, but with additional methods that can operate
on the entire collection of vectors efficiently. :class:`~planar.Vec2Array`
objects are different from Python lists, however, in the following
important ways:

- Vector arrays can contain only :class:`~planar.Vec2` objects.
- Vectors in the arrays are stored in contiguous memory, by value, rather
  than storing references to separate objects as a list does. This means
  that vector arrays use memory more efficiently and are CPU cache-friendly
  for greater performance.
- Arithmetic operations on vector arrays operate as batch operations on
  all vectors in the array.

Vector arrays can be instantiated empty, by calling the class with no arguments.
To instantiate an array pre-populated with vectors, you can pass in any
iterable of 2 number sequences, such as a list of 2-tuples, or 
:class:`~planar.Vec2` objects::

	>>> from planar import Vec2Array
	>>> a = Vec2Array()
	>>> len(a)
	0
	>>> a = Vec2Array([(-1,0), (4,2), (5,-2)])
	>>> len(a)
	3

Vector arrays support the typical list operations you are already familiar with
such as :meth:`append`, :meth:`insert`, and :meth:`extend`::

	>>> from planar import Vec2Array
	>>> a = Vec2Array()
	>>> a.append((4, 3))
	>>> a.insert(0, (5, 5))
	>>> a.extend([(9, -2), (-3, -3)])
	>>> a
	Vec2Array([(5, 5), (4, 3), (9, -2), (-3, -3)])

Item access and a full complement of slicing operations are also supported::

	>>> from planar import Vec2Array
	>>> a = Vec2Array([(0,0), (1,1), (2,2), (3,3), (4,4)])
	>>> a[-1]
	Vec2(4, 4)
	>>> a[1:-1]
	Vec2Array([(1, 1), (2, 2), (3, 3)])
	>>> a[::2]
	Vec2Array([(0, 0), (2, 2), (4, 4)])
	>>> a[4:1:-1]
	Vec2Array([(4, 4), (3, 3), (2, 2)])

Vector arrays are designed to provide efficient batch arithmetic on vectors.
You can perform arithmetic between vector arrays and scalars, single vectors,
other arrays, and :class:`~planar.Affine` transforms. Multiplying an array 
scales all of its constituent vectors::


	>>> from planar import Vec2Array
	>>> a = Vec2Array([(2, 1), (4, 2.5), (3, -1)])
	>>> a * 3
	Vec2Array([(6, 3), (12, 7.5), (9, -3)])
	>>> a * (4, 2)
	Vec2Array([(8, 2), (16, 5), (12, -2)])

Division operates similarly. Addition and subtraction operate componentwise as
in single :class:`~planar.Vec2` objects. You can also perform arithmetic
between vector arrays with the same length. This simply performs the operation
between each element of both arrays in turn::
	
	>>> from planar import Vec2Array
	>>> a = Vec2Array([(-1,0), (1,2), (3,4)]) 
	>>> b = Vec2Array([(3,2), (2,1), (1,0)])
	>>> a + b
	Vec2Array([(2, 2), (3, 3), (4, 4)])

Arrays can be multiplied by transforms, which transforms each vector
therein::

	>>> from planar import Vec2Array, Affine
	>>> a = Vec2Array([(-1, 0), (0, 1), (1, 0), (0, -1)])
	>>> t = Affine.rotation(90) * Affine.scale(2)
	>>> a * t
	Vec2Array([(0, -2), (-2, 0), (0, 2), (2, 0)])

Vector arrays also have methods to retrieve the longest and shortest
member vectors, normalize, or clamp vectors en masse. See the
:class:`~planar.Vec2Array` class reference for details.

