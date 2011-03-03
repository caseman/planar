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
import planar


class Line(object):
    """Infinite directed line.

    :param point: A point on the line.
    :type point: Vec2
    :param direction: Direction of the line as a vector, must not
        be null. Does not need to be unit-length.
    :param direction: Vec2
    """
    def __init__(self, point, direction):
        self.direction = direction
        self.offset = planar.Vec2(*point).dot(self.normal)
    
    @classmethod
    def from_points(cls, points):
        """Create a line from two or more collinear points.  The direction of
        the line is derived from the first two distinct points, the order of
        the remaining points is unimportant.
        
        :param points: Iterable of at least 2 distinct points.
        """
        points = iter(points)
        try:
            start = end = planar.Vec2(*points.next())
            while end == start:
                end = planar.Vec2(*points.next())
        except (StopIteration, TypeError):
            raise ValueError("Expected iterable of 2 or more distinct points")
        line = object.__new__(cls)
        line.direction = end - start
        line.offset = start.dot(line.normal)
        for p in points:
            if not line.point_collinear(p):
                raise ValueError("All points provided must be collinear")
        return line
    
    @classmethod
    def from_normal(cls, normal, offset):
        """Create a line given a normal vector perpendicular to it, at the
        specified distance from the origin. 

        :param normal: A non-null vector perpendicular to the line.
            Does not need to be unit-length.
        :type normal: Vec2
        :param offset: The distance from the line to the origin.
        :type offset: float
        """
        line = object.__new__(cls)
        line.normal = normal
        line.offset = offset
        return line
    
    offset = 0
    """Distance from the origin to the line"""

    @property
    def direction(self):
        """Direction of the line as a unit vector. You may set this
        atribute to any non-null vector, however it will be normalized
        to unit-length.
        """
        return self._direction
    
    @direction.setter
    def direction(self, value):
        direction = planar.Vec2(*value).normalized()
        if direction.is_null:
            raise ValueError("Line direction vector must not be null")
        self._direction = direction
        self._normal = -direction.perpendicular()

    @property
    def normal(self):
        """Normal unit vector perpendicular to the line. You may set this
        atribute to any non-null vector, however it will be normalized
        to unit-length. Modifying this will also affect the direction
        vector accordingly.
        """
        return self._normal

    @normal.setter
    def normal(self, value):
        normal = planar.Vec2(*value).normalized()
        if normal.is_null:
            raise ValueError("Line normal vector must not be null")
        self._normal = normal
        self._direction = normal.perpendicular()
    
    def distance_to(self, point):
        """Return the signed distance from the line to the specified point.
        The sign indicates which half-plane contains the point. If the
        distance is negative, the point is in the "left" half plane with
        respect to the line, if it is positive, the point is in the "right"
        half plane.

        :param point: The point to measure the distance to.
        :type point: Vec2
        """
        point = planar.Vec2(*point)
        return point.dot(self._normal) - self.offset
    
    def point_left(self, point):
        """Return True if the specified point is in the half plane
        to the left of the line.
        """
        return self.distance_to(point) <= -planar.EPSILON
    
    def point_right(self, point):
        """Return True if the specified point is in the half plane
        to the right of the line.
        """
        return self.distance_to(point) >= planar.EPSILON
    
    def point_collinear(self, point):
        """Return True if the specified point is on the line."""
        return abs(self.distance_to(point)) < planar.EPSILON
    
    def parallel(self, point):
        """Return a line parallel to this one that passes through the 
        given point.

        :param point: A point on the parallel line.
        :type point: Vec2
        """
        return Line(point, self.direction)
    
    def perpendicular(self, point):
        """Return a line perpendicular to this one that passes through the
        given point. The orientation of this line is consistent with
        :meth:`planar.Vec2.perpendicular`.

        :param point: A point on the perpendicular line.
        :type point: Vec2
        """
        return Line(point, self.direction.perpendicular())

    def project(self, point):
        """Compute the projection of a point onto the line. This
        is the closest point on the line to the specified point.

        :param point: The point to project.
        :type point: Vec2
        """
        parallel = self.direction.project(point)
        return parallel + self._normal * self.offset

    def reflect(self, point):
        """Reflect a point across the line.

        :param point: The point to reflect.
        :type point: Vec2
        """
        point = planar.Vec2(*point)
        offset_distance = point.dot(self._normal) - self.offset
        return point - 2.0 * self._normal * offset_distance

    def __str__(self):
        """Concise string representation."""
        return "Line(%s, %s)" % (
            tuple(self.project((0,0))), tuple(self.direction))

    def __repr__(self):
        """Precise string representation."""
        return "Line(%r, %r)" % (
            tuple(self.project((0,0))), tuple(self.direction))


# vim: ai ts=4 sts=4 et sw=4 tw=78

