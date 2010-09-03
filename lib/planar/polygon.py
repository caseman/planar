#############################################################################
# Copyright (c) 2010 by Casey Duncan
# Portions copyright (c) 2009 The Super Effective Team 
#                             (www.supereffective.org)
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
import itertools
import planar
from planar.util import cached_property, assert_unorderable

class Polygon(planar.Seq2):
    """Arbitrary polygon represented as a list of vertices. 

    The individual vertices of a polygon are mutable, but the number
    of vertices is fixed at construction.

    :param vertices: Iterable containing three or more :class:`~planar.Vec2` 
        objects.
    """

    def __init__(self, vertices):
        super(Polygon, self).__init__(vertices)
        if len(self) < 3:
            raise ValueError("Polygon(): minimum of 3 vertices required")
        self._clear_cached_properties()

    def _clear_cached_properties(self):
        if len(self) > 3:
            self._convex = _unknown
            self._simple = _unknown
        else:
            self._convex = True
            self._simple = True
        self._degenerate = _unknown
        self._bbox = None

    @property
    def bounding_box(self):
        """The bounding box of the polygon"""
        if self._bbox is None:
            self._bbox = planar.BoundingBox(self)
        return self._bbox

    @property
    def is_convex(self):
        """True if the polygon is convex.

        If this is unknown then it is calculated from the vertices
        of the polygon and cached. Runtime complexity: O(n)
        """
        if self._convex is _unknown:
            self._classify()
        return self._convex

    @property
    def is_convex_known(self):
        """True if the polygon is already known to be convex or not.

        If this value is True, then the value of ``is_convex`` is 
        cached and does not require additional calculation to access.
        Mutating the polygon will invalidate the cached value.
        """
        return self._convex is not _unknown

    def _iter_as_triples(self):
        """Iterate the vertices of the polygon as triples stepping
        forward a single vertex each step
        """
        for i in range(len(self) - 1):
            yield self[i - 1], self[i], self[i + 1]
        yield self[i], self[i + 1], self[0]

    def _iter_edge_vectors(self):
        """Iterate the edges of the polygon as vectors
        """
        for i in range(len(self)):
            yield self[i] - self[i - 1]

    def _classify(self):
        """Calculate the polygon convexity, winding direction,
        detecting and handling degenerate cases.

        Algorithm derived from Graphics Gems IV.
        """
        dir_changes = 0
        angle_sign = 0
        is_null = True
        self._convex = True
        self._winding = 0
        last_delta = self[-1] - self[-2]
        last_dir = (
            (last_delta.x > 0) * -1 or
            (last_delta.x < 0) * 1 or
            (last_delta.y > 0) * -1 or
            (last_delta.y < 0) * 1) or 0
        for delta in itertools.ifilter(
            lambda v: v, self._iter_edge_vectors()):
            is_null = False
            this_dir = (
                (delta.x > 0) * -1 or
                (delta.x < 0) * 1 or
                (delta.y > 0) * -1 or
                (delta.y < 0) * 1) or 0
            dir_changes += (this_dir == -last_dir)
            last_dir = this_dir
            cross = last_delta.cross(delta)
            if cross > 0.0: # XXX Should this be cross > planar.EPSILON?
                if angle_sign == -1:
                    self._convex = False
                    break
                angle_sign = 1
            elif cross < 0.0:
                if angle_sign == 1:
                    self._convex = False
                    break
                angle_sign = -1
            last_delta = delta
        if dir_changes <= 2:
            self._winding = angle_sign
        else:
            self._convex = False
        self._simple = self._convex or _unknown
        self._degenerate = is_null or not angle_sign

    @property
    def is_simple(self):
        """True if the polygon is simple, i.e., it has no self-intersections.

        If this is unknown then it is calculated from the vertices
        of the polygon and cached. 
        Runtime complexity: O(n) (convex), O(n^2) (concave)
        """
        if self._simple is _unknown:
            if self._convex is _unknown:
                self._classify()
            if self._simple is _unknown:
                self._check_is_simple()
        return self._simple
    
    @property
    def is_simple_known(self):
        """True if the polygon is already known to be simple or not.

        If this value is True, then the value of ``is_simple`` is 
        cached and does not require additional calculation to access.
        Mutating the polygon will invalidate the cached value.
        """
        return self._simple is not _unknown

    def _segments_intersect(self, a, b, c, d):
        """Return True if the line segment a->b intersects with
        line segment c->d
        """
        dir1 = (b.x - a.x)*(c.y - a.y) - (c.x - a.x)*(b.y - a.y)
        dir2 = (b.x - a.x)*(d.y - a.y) - (d.x - a.x)*(b.y - a.y)
        if (dir1 > 0.0) != (dir2 > 0.0) or (not dir1) != (not dir2): 
            dir1 = (d.x - c.x)*(a.y - c.y) - (a.x - c.x)*(d.y - c.y)
            dir2 = (d.x - c.x)*(b.y - c.y) - (b.x - c.x)*(d.y - c.y)
            return ((dir1 > 0.0) != (dir2 > 0.0) 
                or (not dir1) != (not dir2))
        return False

    def _check_is_simple(self):
        """Check the polygon for self-intersection and cache the result
        """
        segments = [(self[i - 1], self[i]) for i in range(len(self))]
        intersects = self._segments_intersect
        a, b = segments.pop()
        # Ignore adjacent edges which cannot intersect
        for c, d in segments[1:-1]:
            if intersects(a, b, c, d):
                self._simple = False
                return
        a, b = segments.pop()
        while len(segments) > 1:
            next = segments.pop()
            for c, d in segments:
                if intersects(a, b, c, d):
                    self._simple = False
                    return
            a, b = next
        self._simple = True

    def __setitem__(self, index, vert):
        super(Polygon, self).__setitem__(index, vert)
        self._clear_cached_properties()


_unknown = object()
