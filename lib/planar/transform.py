#############################################################################
# Copyright (c) 2010 by Casey Duncan
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, 
#   this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# * Neither the name(s) of the copyright holders nor the names of its
#   contributors may be used to endorse or promote products derived from this
#   software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AS IS AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL THE COPYRIGHT HOLDERS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, 
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#############################################################################

from __future__ import division

import math
import planar
from planar.util import cached_property, assert_unorderable


class Affine(tuple):
    """Two dimensional affine transform for linear mapping from 2D coordinates
    to other 2D coordinates. parallel lines are preserved by these
    transforms. Affine transforms can perform any combination of translations,
    scales/flips, shears, and rotations.  Class methods are provided to
    conveniently compose tranforms from these operations.

    Internally the transform is stores as a 3x3 transformation matrix.  The
    transform may be constructed directly by specifying the first two rows of
    matrix values as 6 floats. Since the matrix is an affine transform, the
    last row is always ``(0, 0, 1)``.
    
    :param members: 6 floats for the first two matrix rows.
    :type members: float
    """

    def __new__(self, *members):
        if len(members) == 6:
            mat3x3 = [x * 1.0 for x in members] + [0.0, 0.0, 1.0]
            return tuple.__new__(Affine, mat3x3)
        else:
            raise TypeError(
                "Expected 6 number args, got %s" % len(members))

    @classmethod
    def identity(self):
        """Return the identity transform

        :rtype: Affine
        """
        return identity

    @classmethod
    def translation(self, offset):
        """Create a translation transform from an offset vector.

        :param offset: Translation offset.
        :type offset: :class:`~planar.Vec2`
        :rtype: Affine
        """
        ox, oy = offset
        return tuple.__new__(Affine, 
            (1.0, 0.0, ox, 
             0.0, 1.0, oy,
             0.0, 0.0, 1.0))

    @classmethod
    def scale(self, scaling, anchor=None):
        """Create a scaling transform from a scalar or vector,
        optionally about an anchor point.

        :param scaling: The scaling factor. A scalar value will
            scale in both dimensions equally. A vector scaling
            value scales the dimensions independently.
        :type scaling: float or :class:`~planar.Vec2`
        :param anchor: Point to scale relative to. If omitted,
            the scaling is with respect to the origin.
        :rtype: Affine
        """
        try:
            sx = sy = float(scaling)
        except TypeError:
            sx, sy = scaling
        if anchor is None:
            return tuple.__new__(Affine, 
                (sx, 0.0, 0.0,
                 0.0, sy, 0.0,
                 0.0, 0.0, 1.0))
        else:
            ax, ay = anchor
            return tuple.__new__(Affine, 
                (sx, 0.0, sx * ax - ax,
                 0.0, sy, sy * ay - ay,
                 0.0, 0.0, 1.0))
            
    @classmethod
    def shear(self, shearing, anchor=None):
        """Create a shear transform from a vector,
        optionally about an anchor point.

        :param shearing: The x and y shearing amount.
        :type shearing: :class:`~planar.Vec2`
        :param anchor: Point to shear relative to. If omitted,
            the shear is with respect to the origin.
        :rtype: Affine
        """
        sx, sy = shearing
        if anchor is None:
            return tuple.__new__(Affine, 
                (1.0, sx, 0.0,
                 sy, 1.0, 0.0,
                 0.0, 0.0, 1.0))
        else:
            ax, ay = anchor
            return tuple.__new__(Affine, 
                (1.0, sx, sx * ay,
                 sy, 1.0, sy * ax,
                 0.0, 0.0, 1.0))

    @classmethod
    def rotation(self, angle, pivot=None):
        """Create a rotation transform at the specified angle,
        optionally about the specified pivot point.

        :param angle: Rotation angle in degrees
        :type angle: float
        :param pivot: Point to rotate about, if omitted the
            rotation is about the origin.
        :type pivot: :class:`~planar.Vec2`
        :rtype: Affine
        """
        angle = math.radians(angle)
        sa = math.sin(angle)
        ca = math.cos(angle)
        if pivot is None:
            return tuple.__new__(Affine, 
                (ca, sa, 0.0,
                -sa, ca, 0.0,
                 0.0, 0.0, 1.0))
        else:
            px, py = pivot
            return tuple.__new__(Affine,
                (ca, sa, ca*px + sa*py - px,
                -sa, ca, ca*py - sa*px - py,
                 0.0, 0.0, 1.0))

    def __str__(self):
        """Concise string representation."""
        return ("|% .2f,% .2f,% .2f|\n"
                "|% .2f,% .2f,% .2f|\n"
                "|% .2f,% .2f,% .2f|") % self

    def __repr__(self):
        """Precise string representation."""
        return ("Affine(%r, %r, %r,\n"
                "       %r, %r, %r,\n"
                "       %r, %r, %r)") % self

    @cached_property
    def determinant(self):
        """The determinant of the transform matrix. This value
        is equal to the area scaling factor when the transform
        is applied to a shape.
        """
        a, b, c, d, e, f, g, h, i = self
        return a*e - b*d

    @cached_property
    def is_identity(self):
        """True if this transform equals the identity matrix,
        within rounding limits."""
        return self is identity or self.almost_equals(identity)

    @cached_property
    def is_rectilinear(self):
        """True if the transform is rectilinear, i.e., whether
        a shape would remain axis-aligned, within rounding 
        limits, after applying the transform.
        """
        a, b, c, d, e, f, g, h, i = self
        return ((abs(a) < planar.EPSILON and abs(e) < planar.EPSILON) 
            or (abs(d) < planar.EPSILON and abs(b) < planar.EPSILON))

    @cached_property
    def is_degenerate(self):
        """True if this transform is degenerate, which means that it will
        collapse a shape to an effective area of zero. Degenerate transforms
        cannot be inverted.
        """
        return abs(self.determinant) < planar.EPSILON

    @cached_property
    def column_vectors(self):
        """The values of the transform as three 2D column vectors"""
        a, b, c, d, e, f, _, _, _ = self
        return planar.Vec2(a, d), planar.Vec2(b, e), planar.Vec2(c, f)

    def almost_equals(self, other):
        """Compare transforms for approximate equality.

        :param other: Transform being compared.
        :type other: Affine
        :return: True if absolute difference between each element
            of each respective tranform matrix < ``EPSILON``.
        """
        for i in (0, 1, 2, 3, 4, 5):
            if abs(self[i] - other[i]) >= planar.EPSILON:
                return False
        return True

    def __gt__(self, other):
        return assert_unorderable(self, other)

    __ge__ = __lt__ = __le__ = __gt__

    # Override from base class. We do not support entrywise
    # addition, subtraction or scalar multiplication because
    # the result is not an affine transform

    def __add__(self, other):
        raise TypeError("Operation not supported")

    __iadd__ = __add__

    def __mul__(self, other):
        """Apply the transform using matrix multiplication, creating a
        resulting object of the same type.  A transform may be applied to
        another transform, a vector, vector array, or shape.

        :param other: The object to transform.
        :type other: Affine, :class:`~planar.Vec2`, 
            :class:`~planar.Vec2Array`, :class:`~planar.Shape`
        :rtype: Same as ``other``
        """
        sa, sb, sc, sd, se, sf, _, _, _ = self
        if isinstance(other, Affine):
            oa, ob, oc, od, oe, of, _, _, _ = other
            return tuple.__new__(Affine, 
                (sa*oa + sb*od, sa*ob + sb*oe, sa*oc + sb*of + sc,
                 sd*oa + se*od, sd*ob + se*oe, sd*oc + se*of + sf,
                 0.0, 0.0, 1.0))
        elif isinstance(other, planar.Vec2):
            vx, vy = other
            return planar.Vec2(vx*sa + vy*sb + sc, vx*sd + vy*se + sf)
        elif hasattr(other, 'from_points'):
            Point = planar.Point
            return other.from_points(
                Point(px*sa + py*sb + sc, px*sd + py*se + sf)
                for px, py in other)
        return NotImplemented
    
    def __rmul__(self, other):
        """Apply the transform using matrix multiplication, creating a
        resulting object of the same type.  A transform may be applied to
        another transform, a vector, vector array, or shape.

        :param other: The object to transform.
        :type other: Affine, :class:`~planar.Vec2`, 
            :class:`~planar.Vec2Array`, :class:`~planar.Shape`
        :rtype: Same as ``other``
        """
        sa, sb, sc, sd, se, sf, _, _, _ = self
        if isinstance(other, Affine):
            oa, ob, oc, od, oe, of, _, _, _ = other
            return tuple.__new__(Affine, 
                (oa*sa + ob*sd, oa*sb + ob*se, oa*sc + ob*sf + oc,
                 od*sa + oe*sd, od*sb + oe*se, od*sc + oe*sf + of,
                 0.0, 0.0, 1.0))
        else:
            return self.__mul__(other)

    def __imul__(self, other):
        if isinstance(other, Affine) or isinstance(other, planar.Vec2):
            return self.__mul__(other)
        else:
            return NotImplemented

    def __invert__(self):
        """Return the inverse transform.
        
        :raises: :except:`TransformNotInvertible` if the transform
            is degenerate.
        """
        if self.is_degenerate:
            raise planar.TransformNotInvertibleError(
                "Cannot invert degenerate transform")
        idet = 1.0 / self.determinant
        sa, sb, sc, sd, se, sf, _, _, _ = self
        ra = se * idet
        rb = -sb * idet
        rd = -sd * idet
        re = sa * idet
        return tuple.__new__(Affine, 
            (ra, rb, -sc*ra - sf*rb,
             rd, re, -sc*rd - sf*re,
             0.0, 0.0, 1.0))

    __hash__ = tuple.__hash__ # hash is not inherited in Py 3


identity = Affine(1, 0, 0, 0, 1, 0)
"""The identity transform"""


# vim: ai ts=4 sts=4 et sw=4 tw=78
