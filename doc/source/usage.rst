Usage Guide
===========

Importing Classes
-----------------

Generally you will want to import classes directly from the top-level
``planar`` package, or simply import the package itself::

	from planar import Vec2
	v = Vec2(5, 4)

or::

	import planar
	v = planar.Vec2(5, 4)

Doing this will give you the most efficient implementation available of each
class where the program is being run. It will provide the native-code
implementation where available, falling back to the pure-Python reference
implementation if necessary. This insulates your program from the particulars
of the run-time environment.

If desired, you can import a particular implementation directly from the
modules under the ``planar`` package. The Python implementations are in
plainly named modules::

	from planar.vector import Vec2 # Python implementation

The C implementations are in similarly named modules prefixed with "c"::

	from planar.cvector import Vec2 # C implementation

Generally, however, it is best to simply import things directly from the
``planar`` package. Relying on the vagaries of either implementation in your
application is not recommended.

Also, you should avoid mixing usage of both implementations of a ``planar``
class in a single app (see below for details why). If you simply import them
from the ``planar`` package directly, you won't have to worry about this.

Implementation Differences
--------------------------

In general, the Python and C implementations of each class should be virtually
identical from the application's standpoint. Efforts have been made to ensure
this is true. However, practical considerations mean there are some subtle
differences that you should be aware of. Applications should not rely on these
implementation details for correct operation:

- Python implementations may be based on highly general base-classes (e.g.,
  tuple) whereas the C implementations are not. You should not rely on
  specific base-classes, except where documented here, and you should
  not rely on any specific inherited behavior that is not documented.
  For instance, the Python ``Vec2`` implementation derives from ``tuple``,
  thus it supports operations like slicing, ``in`` and :meth:`count`,
  whereas the C implementation does not.

- Exception message strings will vary according to implementation. As with
  Python itself, exception messages are not considered part of the canonical
  API, and applications should not rely on their content.

- Some C APIs may not support keyword arguments, whereas all Python APIs do.
  For example ``planar.Vec2(x=1, y=2)`` will work with the Python
  implementation, but not the C implementation. All APIs with optional
  arguments support both positional and keyword arguments. For example:
  ``planar.Vec2.polar(angle=45, length=10)`` is fully supported by both.

.. note:: Use of positional arguments is often optimized and significantly
	faster in the C implementations.

- Instances of C-implemented classes do not have instance dictionaries,
  whereas all Python implementations do. In Python, they are often used for
  caching property values for repeated access. In C they are omitted for
  efficiency. This means that application code should not assign arbitrary
  attributes onto ``planar`` instances. If you need such functionality, you
  should subclass the ``planar`` class within your application. Such
  subclasses, will always have an instance dict regardless of the base-class
  implementation.

- Hashable objects, such as ``Vec2`` may not hash to the same value in their C
  and Python implementations. This is because the Python hash method is often
  derived from the generic ``tuple`` hash method, whereas the C hash method is
  a less-general, more efficient hash. In practical terms this means you
  cannot put ``cvector.Vec2``, and ``vector.Vec2`` instances into the same
  ``dict`` or ``set`` with satisfactory results.

- Like tuples, and floats, among others, ``planar`` object instances may be
  pooled and recycled for efficiency. You should not rely on the results of
  the ``is`` operator between ``planar`` objects.

If you run across other implementation differences than the above, 
`let us know <http://groups.google.com/group/grease-users>`_. 
They are either a bug or they should be documented.
