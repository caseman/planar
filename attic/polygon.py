"""Unused polygon algorithms"""

class Polygon(planar.Seq2):

    def _check_is_simple_brute_force(self):
        """Check the polygon for self-intersection and cache the result
        """
        segments = [(self[i - 1], self[i]) for i in range(len(self))]
        intersects = self._segments_intersect
        a, b = segments.pop()
        # Ignore adjacent edges which cannot intersect
        for c, d in segments[1:-1]:
            if intersects(a, b, c, d):
                self._simple = False
                return False
        a, b = segments.pop()
        while len(segments) > 1:
            next = segments.pop()
            for c, d in segments:
                if intersects(a, b, c, d):
                    self._simple = False
                    return False
            a, b = next
        self._simple = True
        return True

    def _pnp_crossing_test(self, point):
        """Return True if the point is in the polygon using a crossing
        test. This is a general point-in-poly test and will work
        correctly with all polygons.

        The general idea of this algorithm is to cast a ray from the point
        along the +x axis, counting the number of polygon edges crossed.
        An odd number of crossings means that the point is in the polygon.

        This algorithm is based on the "crossings multiply" algorithm
        available here:
        http://tog.acm.org/resources/GraphicsGems/gemsiv/ptpoly_haines/ptinpoly.c

        Complexity: O(n)
        """
        px, py = point
        is_inside = False
        v0_x, v0_y = self[-1]
        v0_above = (v0_y >= py)
        for v1_x, v1_y in self:
            v1_above = (v1_y >= py)
            if (v0_above != v1_above
                and ((v1_y - py) * (v0_x - v1_x) >=
                    (v1_x - px) * (v0_y - v1_y)) == v1_above):
                is_inside = not is_inside
            v0_above = v1_above
            v0_x = v1_x
            v0_y = v1_y
        return is_inside

