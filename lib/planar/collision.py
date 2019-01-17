#############################################################################
# Copyright (c) 2018 by Casey Duncan
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

from collections import deque
import math
import planar
from planar import sh_op as op


class CollisionResult(object):

    space = None
    """CollisionSpace being queried"""

    query = None
    """Object or objects being tested for collision with the space"""

    def __nonzero__(self):
        """true if there are any collision results. Often faster to
        calculate than the full results.
        """

    def __len__(self):
        """Collision result count"""

    def __iter__(self):
        """Iterates collision results. Allows calculations to be done lazily
        and incrementally and may be cheaper when full results are not
        usually needed.
        """

    def one(self):
        """Calculate and return one collision result only. If there are
        multiple results the one returned is arbitrary. If there were no
        collisions, return None. Useful for convenience when you expect only
        one result
        """

    def all(self):
        """Calculate and return a sequence containing all collision results.
        Generally cached once calculated so subsequent calls don't need
        to recompute
        """

    def candidates(self):
        """Return an iterable of candidate results that could be in
        colliision, but without doing fine-grained pairwise checks. This
        allows a coarse collision calculation that is typically very fast,
        though can return false positives. This may be useful if raw speed is
        more important than absolute accuracy, or as an input to a
        custom fine-grained collision detection algorithm
        """

def _unique_pairs(pairs):
    """Given an iterable of object pairs, generate only unique pairs
    irrespective of pair ordering. Thus (a, b) is not unique from (b, a), and
    would only be output once.

    Objects are considered unique based on identity. No object comparison
    is performed.
    """
    seen = {}
    for p in pairs:
        a, b = p
        a_id = id(a)
        b_id = id(b)
        pkey = (a_id, b_id) if a_id < b_id else (b_id, a_id)
        if pkey not in seen:
            seen[pkey] = True
            yield p

class _QuadTreeNode(object):
    """Internal node class for QuadTreeSpace"""
    __slots__ = ('center', 'size', 'members', 'child')

    def __init__(self, center, size, members, child):
        self.center = center
        self.size = size
        self.members = members
        self.child = child

class QuadTreeSpace(object):
    """Collision space that organizes shapes into recursively subdivided
    quadrant nodes. This allows operations to grow in cost logarithmically
    with the number of shapes rather than linearly or exponentially.

    Quad-trees are particularly efficient for relatively static shapes with
    highly varying sizes and uneven distributions.

    Due to traversal costs, adds, removes, and updates may be more expensive
    for quad-trees than other types of spaces. They are best with a more
    stable set of shapes.
    """

    bounding_box = None
    """Bounding box enclosing all shapes in the space"""

    node_capcity = None
    """Number of shapes held in a leaf node before subdividing. Lower values
    can result in fewer shape comparisons to detect collisions but can
    increase the depth of the tree resulting in more traversal cost and memory
    usage. A larger value could be used for simple shapes that have cheaper
    collision checks. Using the highest value that results in acceptable
    performance is generally best, but this will vary by application.

    This value is not an absolute cap. In cases where shapes cover a
    significant fraction of a node's area, or when many shapes largely
    overlap in a node, there may be no benefit to subdividing the node
    further. In such cases nodes may significantly exceed the node_capacity
    value. The `stats()` method can be used to see if this is occurring.
    """

    implicit_updates = True
    """Flag determining if shape positions will be updated opportunistically
    when the quad-tree structure is rearranged, such as during add and optimize
    operations. This may result in an inconsistent tree state where some shapes
    reflect their current positions whereas others reflect a stale previous
    position until `update()` is called. The benefit is that less overall work 
    is needed to keep the tree state updated.

    Disabling this ensures that shape positions in the tree are only
    updated when the `update()` method is called, resulting in a consistent
    tree state, at the expense of more expensive updates. If your application
    relies on using the space to determine shapes that moved, or to
    operate using past shape positions consistently, then you should set this
    to False.

    If your application only uses the space in an updated state, then 
    implicit updates can improve performance. This is typically the common
    case.
    """

    def __init__(self, node_capacity=4, implicit_updates=True):
        """"Initialize the QuadTree

        node_capacity -- Number of shapes allowed in a leaf node until it is
        considered for subdividing. See the `node_capacity` attribute for
        details.

        implicit_updates -- If True, shape positions will be updated
        opportunistically when the quad-tree structure changes. This
        improves update performance at the cost of consistency. See the
        `implicit_updates` attribute for details.
        """
        self.node_capacity = node_capacity
        self.implicit_updates = implicit_updates
        self._qtree = _QuadTreeNode(None, 0, [], None)
        self._members_to_nodes = {}
        self._members_to_bbox = {}
        self._tree_bounds = None # power of 2 bounding square for entire tree

    def __contains__(self, shape):
        """Return True if shape is in the space"""
        return shape in self._members_to_nodes

    def __len__(self):
        """Return the number of shapes in the space"""
        return len(self._members_to_nodes)

    def __iter__(self):
        """Return an iterator of all shapes in the space"""
        return self._members_to_nodes.iterkeys()

    def add(self, *shape):
        """Add one or more shapes to the space"""
        # Add the boxes first to avoid clobbering existing member positions
        for member in shape:
            # Check _members_to_nodes in case the shape was previously
            # added as static and now is being added again
            if member not in self._members_to_nodes:
                self._members_to_bbox[member] = member.bounding_box

        self.add_static(*shape)

    def add_static(self, *shape):
        """Add one or more "static" shapes to the space. These shapes will be
        excluded from incremental updates but can be updated explicitly if
        needed. This is useful for stationary shapes or shapes that move
        or change infrequently.

        Excluding static objects saves time on incremental updates.
        There is also a small memory savings for static shapes since their
        previous location state does not need to be stored.
        """
        if self._tree_bounds is not None:
            new_bb = planar.BoundingBox.from_shapes(self._tree_bounds, *shape)
            if new_bb != self._tree_bounds:
                self._expand_root(new_bb)

        for new_member in shape:
            if new_member not in self._members_to_nodes:
                member_nodes = self._find_nodes_for_member(self._qtree, member)
                self._members_to_nodes[shape] = member_nodes
                for node in member_nodes:
                    node.members.append(member)

        if self.bounding_box is not None:
            self.bounding_box = planar.BoundingBox.from_shapes(
                self.bounding_box, *shape)
        else:
            self.bounding_box = planar.BoundingBox.from_shapes(*shape)

    def contains_static(self, shape):
        """Return True if shape was added to the space as a static shape"""
        return (shape in self._members_to_nodes and 
                shape not in self._members_to_bbox)

    def _find_nodes_for_member(self, node, member, 
        member_bbox=None, nodes=None):
        """Descend the tree finding nodes suitable for member, return the
        nodes found.
        """
        if nodes is None:
            nodes = []

        if member_bbox is None:
            if not self.implicit_updates:
                member_bbox = self._members_to_bbox.get(member)
            if member_bbox is None:
                member_bbox = member.bounding_box

        large_node_overlap = (
            node.center is not None and # Initial root node has no center
            member_bbox.contains_point(node.center) and
            member_bbox.width * node.bbox.height * 2 > node.size * node.size)

        found_leaf_node = (not node.child and 
            len(node.members) < self.node_capacity)

        if not node.child and not large_node_overlap and not found_leaf_node:
            # Leaf node does not have capacity, attempt to split
            found_leaf_node = not self._split(node)

        if found_leaf_node or large_node_overlap:
            # Member goes here, end descent
            nodes.append(node)
        else:
            # Descend to intersecting child nodes
            center_x, center_y = node.center
            if member_bbox.min.x <= center_x:
                if member_bbox.min.y <= center_y:
                    self._find_nodes_for_member(node.child[0], member,
                        member_nodes, member_bbox, nodes)
                if member_bbox.max.y > center_y:
                    self._find_nodes_for_member(node.child[2], member,
                        member_nodes, member_bbox, nodes)
            if member_bbox.max.x > center_x:
                if member_bbox.min.y <= center_y:
                    self._find_nodes_for_member(node.child[1], member,
                        member_nodes, member_bbox, nodes)
                if member_bbox.max.y > center_y:
                    self._find_nodes_for_member(node.child[3], member,
                        member_nodes, member_bbox, nodes)
        return nodes

    def _split(self, node):
        """Split the node into 4 child quads and distribute the members to the
        children where possible. Return False if the node was not actually
        split.

        A node will not split unless enough of its members would be moved down
        to its child nodes. This is to reduce counter-productive tree growth
        in cases where many members overlap a large area of the node, and
        likely each other as well.
        """
        assert not node.child, "Node already split!"
        if node.center is None:
            # Initial root node without center
            # calculate a center and replace the node
            assert node is self._qtree, "Invalid non-root node without center"
            tree_size = max(self.bounding_box.width, self.bounding_box.height)
            # Round size up to nearest power of 2
            # Note this intentionally handles ranges < 1.0
            tree_size = 2**math.ceil(math.log(tree_size, 2))
            self._tree_bounds = planar.BoundingBox.from_center(
                self.bounding_box.center, tree_size, tree_size)
            node = self._qtree = _QuadTreeNode(
                self._tree_bounds.center, tree_size, node.members, [])

        # provisionally create the child nodes
        child_size = node.size * 0.5
        child_offset = node.size * 0.25
        center_x, center_y = node.center
        for dir_x, dir_y in ((-1, -1), (-1, 1), (-1, 1), (1, 1)):
            node.child.append(_QuadTreeNode(
                planar.Vec2(center_x + child_offset * dir_x,
                            center_y + child_offset * dir_y),
                child_size, [], []))

        # Assess the potential split.
        child_moves = 0
        child_dests = {}
        for member in node.members:
            dest = self._find_nodes_for_member(node, member)
            if node not in dest:
                child_moves += 1
                child_dests[member] = dest

        if (child_moves * 4 >= len(node.members) or
            child_moves * 2 >= self.node_capacity):
            # Splitting is not a big win, so bail
            # ditch the empty child nodes so we can try again later
            # TODO look for strategies to avoid rechecking this
            # excessively for pathological cases
            node.child.clear()
            return False

        for member, dest_nodes in child_dests.items():
            self._remove_node_member(node, member)
            for node in dest_nodes:
                node.members.append(member)
                self._members_to_nodes[member].append(node)
            # This is effectively an update for this member
            # so update the cached bounding box if present
            # and implicit updates are enabled
            if self.implicit_updates and member in self._members_to_bbox:
                self._members_to_bbox[member] = member.bounding_box

        return True

    def _remove_node_member(self, node, member):
        try:
            node.members.remove(member)
        except ValueError:
            pass
        try:
            self._members_to_nodes[member].remove(node)
        except ValueError:
            pass

    def _expand_root(self, new_bounds):
        """Expand the tree on the root end until it encloses the new boundary
        """
        old_bounds = self._tree_bounds
        left, bottom = old_bounds.min
        right, top = old_bounds.max
        size = old_bounds.width
        new_left, new_bottom = new_bounds.min
        new_right, new_top = new_bounds.max

        root = self._qtree
        quads = range(4)
        offsets = ((-1,-1), (1, -1), (-1, 1), (1, 1))
        while (left > new_left or 
               right < new_right or 
               bottom > new_bottom or 
               top < new_top):
            if left > new_left:
                quad = 1
                left -= size
            else:
                quad = 0
                right += size
            if bottom > new_bottom:
                quad += 2
                bottom -= size
            else:
                top += size

            center = planar.Vec2((right - left) * 0.5, (top - bottom) * 0.5)
            node = _QuadTreeNode(center, size, [], [])
            for i in quads:
                if i == quad:
                    child = root
                else:
                    offset_x, offset_y = offsets[i]
                    child = _QuadTreeNode(
                        planar.Vec2(center.x + offset_x * size * 0.5,
                                    center.y + offset_y * size * 0.5),
                        size, [], [])
                node.child.append(child)

            root = node
            size *= 2
        self._qtree = root
        self._tree_bounds = planar.BoundingBox.from_center(
            root.center, root.size, root.size)

    def remove(self, *shape):
        """Remove one or more shapes from the space. If the shape
        is not in the space, do nothing
        """
        for member in shape:
            try:
                member_nodes = self._members_to_nodes[member]
            except KeyError:
                continue
            for node in member_nodes:
                node.members.remove(member)
            del self._members_to_nodes[member]
            try:
                del self._members_to_bbox[member]
            except KeyError:
                pass

    def update(self, *shape):
        """Update the space to reflect changes to the shape(s) specified.
        If no shapes are provided, update the tree for all non-static shapes
        that have changed.

        Generally an application should call this method after making changes
        to shapes before performing collision tests.

        raise KeyError if a shape specified is not in the space.

        Note this may be a no-op if the shapes specified have not changed.
        This can be handled most efficiently for non-static shapes.

        Return the number of shapes updated.
        """
        if not shape:
            dirty = self.dirty_shapes()
        else:
            # filter the dirty ones from the provided shapes
            # shapes without a cached bbox are always considered dirty
            last_bbox = self._members_to_bbox.get
            dirty = [s for s in shape if last_bbox(s) != s.bounding_box]

        for member in dirty:
            current_nodes = self._members_to_nodes[member]
            new_nodes = self._find_nodes_for_member(self._qtree, member)
            if new_nodes != current_nodes:
                new_set = set(new_nodes)
                old_set = set(current_nodes)
                for node in (old_set - new_set):
                    node.members.remove(member)
                for node in (new_set - old_set):
                    node.members.append(member)
                self._members_to_nodes[member] = new_nodes
            if member in self._members_to_bbox:
                self._members_to_bbox[member] = member.bounding_box

        return len(dirty)

    def is_dirty(self, shape):
        """Return True if shape is in the space and its position
        state needs to be updated

        Raises KeyError if shape is not in the space, or is static
        """
        return self._members_to_bbox[shape] != shape.bounding_box

    def dirty_shapes(self):
        """Return a generator of all non-static shapes whose position state
        needs to be updated in the space. These are the objects that would be
        updated by a call to `update()` with no arguments.
        """
        for member, last_bbox in self._members_to_bbox.iteritems():
            if last_bbox != member.bounding_box:
                yield member

    def coarse_collide_point(self, point):
        """Return a generator yielding shapes that may be in collision with
        the point specified. No fine-grained collision checking is done so this
        may return false positives.

        Algorithmic complexity: best case O(log n), worst case O(n). The worst
        case occurs if the point collides or nearly collides with all
        shapes in the space.

        The coarse collision methods are useful for implementing a custom
        collision detection system using the space as a fast source of
        collision candidates.
        """
        if self.bounding_box.contains_point(point):
            node = self._qtree
            px, py = point
            while 1:
                for member in node.members:
                    if member.bounding_box.contains_point(point):
                        yield member
                if node.child:
                    index = (px > node.center.x) + (py > node.center.y) * 2
                    node = node.child[index]
                else:
                    break

    def _collect_all(self, node, result):
        """Recursively collect all nodes including node and its children
        into the result sequence
        """
        # This can be written more concisely as a recursive function
        # but doing it iteratively is more efficient
        i = len(result)
        result.append(node)
        try:
            # TODO test if len() check or exception is faster
            while 1:
                result.extend(node.child)
                i += 1
                node = result[i]
        except IndexError:
            return result

    def _collide_nodes(self, node, bbox, result=None):
        """Return all nodes recursively that collide with bbox"""
        if result is None:
            result = []

        center_x, center_y = node.center
        half_size = node.size * 0.5
        if (center_x - bbox.min.x >= half_size and
            center_y - bbox.min.y >= half_size and
            bbox.max.x - center_x >= half_size and
            bbox.max.y - center_y >= half_size):
            # node is completely enclosed
            return self._collect_all(node, result)

        result.append(node)
        if node.child:
            # Descend to intersecting child nodes
            if bbox.min.x <= center_x:
                if bbox.min.y <= center_y:
                    self._collide_nodes(node.child[0], bbox, result)
                if bbox.max.y > center_y:
                    self._collide_nodes(node.child[2], bbox, result)
            if bbox.max.x > center_x:
                if bbox.min.y <= center_y:
                    self._collide_nodes(node.child[1], bbox, result)
                if bbox.max.y > center_y:
                    self._collide_nodes(node.child[3], bbox, result)

        return result

    def _filter_node_members(self, nodes, filter_func):
        """Return a generator of all unique members in nodes where
        `filter_func(member)` returns True
        """
        seen = {}
        for node in nodes:
            for member in node.members:
                if (member not in seen and filter_func(member)):
                    yield member
                seen[member] = True

    def coarse_collide_shape(self, shape):
        """Return a generator yielding shapes that may be in collision with
        the shape specified. No fine-grained collision checking is done so this
        may return false positives.

        This method is optimized if shape is in the space, but it will
        also work for any shape.

        Algorithmic complexity:
          - Best (common) case shape in space: O(1)
          - Common case shape not in space: O(log n)
          - Worst case, many shapes in near collision: O(n)
        """
        shape_bbox = shape.bounding_box

        if shape in self._members_to_nodes:
            nodes = self._members_to_nodes[shape]
        elif op.bbox_collides_bbox(shape_bbox, self.bounding_box):
            nodes = self._collide_nodes(self._qtree, shape_bbox)
        else:
            return

        return self._filter_node_members(nodes,
            lambda m: op.bbox_collides_bbox(shape_bbox, m.bounding_box))

    def _self_collide_node(self, node, seen,
        members_above=frozenset(), members_enclosing=frozenset()):
        if node.members:
            if members_above:
                # Check if any members we found above enclose this node
                # entirely if so they collide with all members here and below
                # by definition, so we don't need to collision check them
                node_bbox = planar.BoundingBox.from_center(
                    node.center, node.size, node.size)
                members_enclosing = members_enclosing.union(
                    (m for m in members_above 
                     if op.bbox_encloses_bbox(m.bounding_box, node_bbox)))

            for a in members_enclosing:
                for b in node.members:
                    pair = (a, b) if id(a) < id(b) else (b, a)
                    if a is not b and pair not in seen:
                        seen[pair] = True
                        yield pair

            members_above = members_above.union(node.members)
            members_above -= members_enclosing
            for a in members_above:
                a_bbox = a.bounding_box
                for b in node.members:
                    if a is not b:
                        pair = (a, b) if id(a) < id(b) else (b, a)
                        if (pair not in seen and
                            op.bbox_collides_bbox(a_bbox, b.bounding_box)):
                            yield pair
                        seen[pair] = True

        for child in node.child:
            # TODO use `yield from` or itertools.chain.from_iterable
            for pair in self._self_collide_node(child, seen,
                members_above, members_enclosing):
                yield pair

    def coarse_self_collide(self):
        """Return a generator yielding pairs of shapes in the space that may
        be in collision. No fine-grained collision checking is done so this
        may return false positives.

        Algorithmic complexity:
          - Best case, low shape overlap: O(n)
          - Common case: O(n log n)
          - Worst case, high shape overlap O(n^2)

        Unless most of the shapes in the space are clustered together in near
        collision, this will perform much better than a brute force check.
        """
        return self._self_collide_node(self._qtree, seen={})

    def coarse_collide_space(self, other):
        """Return a generator yielding pairs of shapes that may be in
        collision between this collision space and the other space specified.
        No fine-grained collision checking is done so this may return false
        positives.
        """
        overlap = op.intersect_bbox_bbox(self.bounding_box, other.bounding_box)
        if overlap is not None:
            seen = {}

            if len(other) * 5 < len(self):
                # swap to put the smaller space "on top"
                self, other = other, self

            def collide_shape(space, shape):
                # Helper function with special optimizations for quad-trees
                if isinstance(space, QuadTreeSpace):
                    # Do a super coarse collision by node and avoid
                    # excessive bounding box checks and unique filtering
                    if shape in space._members_to_nodes:
                        nodes = space._members_to_nodes[shape]
                    else:
                        nodes = space._collide_nodes(
                            space._qtree, shape.bounding_box)
                    # TODO profile generator vs list comprehension here
                    return itertools.chain.from_iterable(
                        (n.members for n in nodes if n.members))
                else:
                    return space.coarse_collide_shape(shape)

            if len(self) * 5 < len(other):
                # highly uneven space size, loop over members of self
                # and check for collisions in other per self member
                for a in collide_shape(self, overlap):
                    a_bbox = a.bounding_box
                    for b in collide_shape(other, a):
                        pair = (a, b) if id(a) < id(b) else (b, a)
                        if (a is not b and pair not in seen and
                            op.bbox_collides_bbox(a_bbox, b.bounding_box)):
                            yield pair
                        seen[pair] = True
                return

            # iterate node by node and check for collisions
            # in that node boundary in the other space
            # TODO this could be enhanced if we tracked the "density"
            # of each node to determine if it would be better to check the
            # entire node area (as now), or just the node members individually
            # TODO Profile if this is actually better than the above for the
            # matched size case
            nodes = deque()
            nodes.append(self._qtree)
            while nodes:
                node = nodes.popleft()
                if node.members:
                    node_bbox = planar.BoundingBox.from_center(
                        node.center, node.size, node.size)
                    if not op.bbox_collides_bbox(node_bbox, overlap):
                        # node outside space overlap, stop descent and move on
                        continue
                    for a in collide_shape(other, node_bbox):
                        a_bbox = a.bounding_box
                        for b in node.members:
                            pair = (a, b) if id(a) < id(b) else (b, a)
                            if (a is not b and pair not in seen and
                                op.bbox_collides_bbox(a_bbox, b.bounding_box)):
                                yield pair
                            seen[pair] = True
                nodes.extend(node.child)

    def collide_enclosed(self, bounding_box):
        """Return a generator yielding shapes that are completely enclosed in
        bounding_box.
        """
        if op.bbox_collides_bbox(bounding_box, self.bounding_box):
            nodes = self._collide_nodes(self._qtree, bounding_box)
            return self._filter_node_members(nodes,
                lambda m: op.bbox_encloses_bbox(bounding_box, m.bounding_box))

    def _decend_tree(self, node, visit_func, *args):
        for child in node.child:
            self._decend_tree(child, visit_func, *args)
        visit_func(node, *args)

    def _visit_remove_enclosed(self, node, bbox, add_result):
        for member in tuple(node.members):
            if op.bbox_encloses_bbox(bbox, member.bounding_box):
                self.remove(member)
                add_result(member)
        for child in node.child:
            if child.members or child.child:
                break
        else:
            # children are empty, prune them
            node.child.clear()

    def remove_enclosed(self, bounding_box, with_results=False):
        """Bulk remove all shapes completely enclosed in bounding_box. Also
        opportunistically optimize the quad-tree structure where possible.

        This is semantically equivalent to:

        `space.remove(*space.collide_enclosed(bounding_box))`

        But is potentially more efficient, particularly if many shapes are
        matched. Also the tree structure can be efficiently optimized at the
        same time, unlike the above.

        :param with_results: Flag, if True, the shapes removed are returned in
        a set. Disabling this increases performance and reduces
        memory consumption somewhat.
        """
        if with_results:
            result = set()
            add_result = result.add
        else:
            result = None
            add_result = lambda x: None

        if op.bbox_collides_bbox(bounding_box, self.bounding_box):
            self._decend_tree(self._qtree, self._visit_remove_enclosed, 
                              bounding_box, add_result)
        return result

    def collide_ray(self, ray, max_distance=None, width=0):
        """Return a CollisionResult containing shapes colliding with the ray.
        The colliding shapes are returned in the order they collide with the
        ray, closest first. This allows you to use this as a ray trace
        operation.

        ray -- the `planar.Ray` object to test for collisions.

        max_distance -- Optional max distance from the start point to perform
        the ray collision.  If omitted, the collision includes the entire
        extent of the space.  Note colliding the entire space is only
        expensive if the entire CollisionResult is consumed and the ray
        collides with a large number of shapes.

        width -- Optional dimensional width of the ray collision test. This
        allows for a wider "beam" to collide against. Shapes this distance or
        less from the ray are considered in collision.
        """
        # Determine if the ray intersects the space bounds
        closest = ray.project(self._qtree.center)
        if self._tree_bounds.contains_point(closest):
            # find intersecting nodes and approximate the relative distance
            # from the node to the ray anchor
            node = self._qtree
            nodes = [((node.center - ray.anchor).length, node)]
            rise = abs(ray.direction.y)
            run = abs(ray.direction.x)
            i = 0
            while i < len(nodes):
                nodes = nodes[i]
                size = node.size * 0.25
                msize = size * rise + size * run
                for child in node.child:
                    closest = ray.project(child.center)
                    if (abs(closest.x - child.center.x) <= size or
                        abs(closest.y - child.center.y) <= size):
                        dist = (child.center - ray.anchor).length - msize
                        nodes.append((dist, child))
                i += 1
            # Order the nodes roughly by distance from ray anchor
            nodes.sort()



    def self_collisions(self):
        """"Return a CollisionResult of all unique pairs of shapes in
        collision in the space.
        """

    def query(self, *objects):
        """Return a CollisionResult of all shapes that are in collision
        with the space. Each object argument may be one of:

        - Vec2 or Point

        - Shape

        - object with a bounding_box attribute

        - another CollisionSpace
        """

    def optimize(self):
        """Optimize the quad-tree consolidating nodes and removing unused or
        under-used branches, potentially reducing tree depth and memory size.
        Useful after many incremental updates to the space. This is a
        potentially expensive operation, but may result in increased
        efficiency in subsequent space operations.

        Note that optimization is most beneficial when many shapes in the
        space have been replaced, significantly changed or redistributed, and
        the original distribution is unlikely to occur again. If the original
        shapes and distributions will re-occur, it may be better to not
        optimize the tree to reduce node churn.

        Incremental optimization is not done generally for this reason. It
        may in fact be more costly overall depending on the application. Not
        performing optimization implicitly also results in more consistent
        run times for incremental operations like add, remove, and update.

        Returns a dictionary summarizing the optimizations that occurred,
        which can be useful to determine how frequently it should be performed
        in the application.
        """

    def _visit_gather_stats(self, node, depth, stats):
        stats.nodes += 1
        stats.depth = max(stats.depth, depth)
        stats._node_sizes.append(len(node.members))
        if len(node.members) > self.node_capacity:
            self.crowded_nodes += 1

        def node_use(node, members=0, subnodes=0):
            members += len(node.members)
            subnodes += len(node.child)
            for child in node.child:
                members, subnodes = node_use(child, members, subnodes)
            return members, subnodes

        if node.child:
            stats.branches += 1
            members, subnodes = node_use(node)
            if not members:
                node.empty_branches += 1
            elif members < subnodes:
                self.underused_branches += 1
        else:
            stats.leaves += 1

        for child in node.child:
            self._visit_gather_stats(child, depth + 1, stats)

    def stats(self):
        """Return a dictionary of statistics of the quad-tree state
        for debugging and optimizing purposes. These stats include information
        about how many nodes would be consolidated or removed by a call to
        `optimize()` along with general tree stats.
        """
        class Stats(object):
            def __init__(self):
                self.nodes = 0
                self.depth = 0
                self.crowded_nodes = 0
                self.unused_branches = 0
                self.underused_branches = 0
                self.node_size_median = None
                self.node_size_mode = None
                self.node_size_max = None
                self.branches = 0
                self.leaves = 0

                self._node_sizes = []

            def summary(self):
                sizes = sorted(self._node_sizes)
                if sizes:
                    self.node_size_median = sizes[len(sizes) // 2]
                    self.node_size_max = sizes[-1]
                    last = None
                    max_run = 0
                    run = 0
                    mode = None
                    for s in sizes:
                        if s > 0:
                            if s == last:
                                run += 1
                            elif run > max_run:
                                mode = last
                                max_run = run
                                run = 0
                            last = s
                    self.node_size_mode = mode or s

                self.crowded_nodes_pct = self.crowded_nodes * 100 // self.nodes
                self.unused_branches_pct = self.unused_branches * 100 // self.branches
                self.underused_branches_pct = self.underused_branches * 100 // self.branches
                self.unused_leaves_pct = self.unused_leaves * 100 // self.leaves

                del summary._node_sizes
                return vars(self)

        stats = Stats()
        self._visit_gather_stats(self._qtree, 0, stats)
        return stats.summary()




