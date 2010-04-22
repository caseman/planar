Planar Overview
===============

Planar is a 2D geometry library for Python. It is intended for use by games
and interactive real-time applications, but is designed to be useful for
most any program that needs a convenient, high-performance geometry API.

Planar is being developed as part of the larger Grease game framework. 
However, it is a standalone library and has no external dependencies besides
Python, and optionally a C compiler.

Planar is purely a math library, presentation, graphical or otherwise is
left up to the application.

Project Goals
-------------

* Do one thing, 2D geometry, and do it well.
* Provide a high-level, clean, Pythonic API.
* All APIs have both a Python reference implementation and a high performance
  implementation in C with the same interface.
* Compatibility with Python 2.6+, and Python 3.1+
* 100% test coverage.
* Full narrative and API reference documentation.
* Platform-independent.
* Release early and often.
* Be responsive to community input.
* Don't take ourselves too seriously.

License
-------

Planar is distributed under the terms of the new BSD license. You are free to
use it for commercial or non-commercial projects with little or no
restriction, all we ask is that:

* Redistributions of the code, in whole or part, retain the original
  copyright notice and license text.
* You do not claim our endorsement of any derived product.

For a complete text of the license see the ``LICENSE.txt`` file in the source
distrbution.

Acknowledgements 
----------------

The API for planar, and some of the code is derived from the excellent 
work done by the Super Effective Team, thanks guys!

* http://www.supereffective.org/pages/Vector-2d-Vector-Library

Requirements
------------

Planar requires Python 2.6, 2.7, 3.1, or better.

To experience the exhilaration of native-code performance, a C compiler is
required. If someone volunteers, binary releases for platforms where this
is not common (you know who you are) will be happily made available.

Downloading Planar
------------------

Planar releases can be downloaded from the python package index (pypi):

* http://pypi.python.org/pypi/planar/

You can get the latest code in development from the planar mercurial 
repository on bitbucket:

* http://bitbucket.org/caseman/planar/

Installation
------------

To build and install Planar from the source distribution or repository use::

    python setup.py install

To install only the pure-Python modules without compiling, use::

	python setup.py build_py install --skip-build

Only performance is sacrificed without the C extensions, all functionality is
still available when using only the pure-Python modules.

Tests
-----

Planar requires nose for testing. You can install it for Python 2.x
using easy_install::

	easy_install nose

For Python 3.x, you can download and install distribute from here:

* http://pypi.python.org/pypi/distribute

For now, you can get a copy of nose3 for Python 3.x, patched to install
properly on Python 3.1 here:

* http://bitbucket.org/caseman/nose3-caseman-fix/get/7c9181ad403d.zip

Once nose is installed you can run the tests from the source directory
using ``nosetests``, first building the C extensions, like so (on Unix)::

	python setup.py build && nosetests -d -w build/lib.*/planar/
	
This runs the tests inside the ``build`` directory so that the C extensions
can be tested. You can put a ``3`` suffix on the ``python`` and ``nosetests``
commands above for Python 3.x. 

Contributing and Getting Support
--------------------------------

Come visit us at the Grease users google group to get help, moral support,
lavish praise, complain bitterly, report a bug, or contribute ideas:

* http://groups.google.com/group/grease-users


