:mod:`planar` -- Global Definitions
===================================

.. module:: planar
   :synopsis: Global Definitions
.. moduleauthor:: Casey Duncan <casey dot duncan at gmail dot com>


.. data:: __versioninfo__

   Package version as a tuple of three integers: 
   ``(major_version, minor_version, bugfix_version)``.

.. data:: __version__

   Package version as a string:
   ``"major_version.minor_version.bugfix_version"``.

.. data:: EPSILON

   Allowed absolute error value for approximate floating point comparison
   operations.

.. data:: EPSILON2

   Squared absolute error value, always ``EPSILON**2``.

.. autofunction:: set_epsilon

.. warning::

   You should only change the ``EPSILON`` value via the :func:`set_epsilon`
   function. Assigning a value to the variable directly will not work
   correctly, and may result in undefined behavior.

