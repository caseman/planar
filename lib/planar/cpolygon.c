/***************************************************************************
* Copyright (c) 2010 by Casey Duncan
* All rights reserved.
*
* This software is subject to the provisions of the BSD License
* A copy of the license should accompany this distribution.
* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
* IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
* FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
****************************************************************************/
#include "Python.h"
#include <float.h>
#include <string.h>
#include "planar.h"

static PlanarPolygonObject *
Poly_alloc_new(PyTypeObject *type, Py_ssize_t size)
{
	PlanarPolygonObject *poly;

	if (size < 3) {
		PyErr_Format(PyExc_ValueError,
			"Polygon: minimum of 3 vertices required");
		return NULL;
	}
	/* Allocate space for extra verts to duplicate the first
	 * and last vert at either end to simplify many operations */
	poly = (PlanarPolygonObject *)type->tp_alloc(type, size + 2);
	if (poly != NULL) {
		Py_SIZE(poly) = size;
		poly->vert = poly->data + 1;
	}
	return poly;
}

static PlanarPolygonObject *
Poly_new(PyTypeObject *type, PyObject *args, PyObject *kwargs)
{
	PyObject *verts_arg, *is_convex_arg = NULL, *is_simple_arg = NULL;
	PyObject *verts_seq = NULL;
	PlanarPolygonObject *poly = NULL;
	Py_ssize_t size, i;

    static char *kwlist[] = {"vertices", "is_convex", "is_simple", NULL};

    if (!PyArg_ParseTupleAndKeywords(
        args, kwargs, "O|OO:Polygon.__init__", kwlist, 
			&verts_arg, &is_convex_arg, &is_simple_arg)) {
        return NULL;
    }
	if (!PySequence_Check(verts_arg)) {
		verts_arg = verts_seq = PySequence_Fast(verts_arg, 
			"expected iterable of Vec2 objects");
		if (verts_seq == NULL) {
			goto error;
		}
	}
	size = PySequence_Size(verts_arg);
	if (size == -1) {
		goto error;
	}
	poly = Poly_alloc_new(type, size);
	if (poly == NULL) {
		goto error;
	}
	if (is_convex_arg != NULL && PyObject_IsTrue(is_convex_arg) > 0 
		|| size == 3) {
		poly->flags = (POLY_CONVEX_FLAG | POLY_CONVEX_KNOWN_FLAG 
			| POLY_SIMPLE_FLAG | POLY_SIMPLE_KNOWN_FLAG);
	} else if (is_simple_arg != NULL && PyObject_IsTrue(is_simple_arg) > 0) {
		poly->flags = POLY_SIMPLE_FLAG | POLY_SIMPLE_KNOWN_FLAG;
	}

    if (PlanarSeq2_Check(verts_arg)) {
		/* Copy existing Seq2 (optimized) */
		memcpy(poly->vert, ((PlanarSeq2Object *)verts_arg)->vec, 
			sizeof(planar_vec2_t) * size);
    } else {
		/* Generic iterable of points */
		for (i = 0; i < size; ++i) {
			if (!PlanarVec2_Parse(PySequence_Fast_GET_ITEM(verts_arg, i), 
				&poly->vert[i].x, &poly->vert[i].y)) {
				PyErr_SetString(PyExc_TypeError,
					"expected iterable of Vec2 objects");
				goto error;
			}
		}
    }
	Py_XDECREF(verts_seq);
	return poly;

error:
	Py_XDECREF(verts_seq);
	Py_XDECREF(poly);
	return NULL;
}

static void
Poly_dealloc(PlanarPolygonObject *self) {
	if (self->lt_y_poly != NULL) {
		PyMem_Free(self->lt_y_poly);
		self->lt_y_poly = NULL;
		self->rt_y_poly = NULL;
	}
    Py_TYPE(self)->tp_free((PyObject *)self);
}

static PlanarPolygonObject *
Poly_new_regular(PyTypeObject *type, PyObject *args, PyObject *kwargs)
{
	Py_ssize_t vert_count, i;
	double radius, angle_step, x, y;
	PyObject *center_arg = NULL;
	double center_x = 0.0, center_y = 0.0;
	double angle = 0.0;
	planar_vec2_t *vert;
	PlanarPolygonObject *poly;

    static char *kwlist[] = {
		"vertex_count", "radius", "center", "angle", NULL};

    if (!PyArg_ParseTupleAndKeywords(
        args, kwargs, "nd|Od:Polygon.regular", kwlist, 
			&vert_count, &radius, &center_arg, &angle)) {
        return NULL;
    }
	if (center_arg != NULL) {
		if (!PlanarVec2_Parse(center_arg, &center_x, &center_y)) {
			PyErr_SetString(PyExc_TypeError,
				"Polygon.regular(): "
				"expected Vec2 object for argument center");
			return NULL;
		}
	}
	poly = Poly_alloc_new(type, vert_count);
	if (poly == NULL) {
		return NULL;
	}
	angle_step = 360.0 / vert_count;
	for (i = 0, vert = poly->vert; i < vert_count; ++i, ++vert) {
		cos_sin_deg(angle, &x, &y);
		vert->x = x * radius + center_x;
		vert->y = y * radius + center_y;
		angle += angle_step;
	}
	poly->centroid.x = center_x;
	poly->centroid.y = center_y;
	x = (poly->vert[0].x + poly->vert[1].x) * 0.5 - center_x;
	y = (poly->vert[0].y + poly->vert[1].y) * 0.5 - center_y;
	poly->min_r2 = x*x + y*y;
	poly->max_r2 = radius * radius;
	poly->flags |= (POLY_CENTROID_KNOWN_FLAG | POLY_DUP_VERTS_KNOWN_FLAG 
		| POLY_CONVEX_KNOWN_FLAG | POLY_CONVEX_FLAG 
		| POLY_SIMPLE_KNOWN_FLAG | POLY_SIMPLE_FLAG
		| POLY_RADIUS_KNOWN_FLAG | POLY_DEGEN_KNOWN_FLAG);
	if (radius == 0.0) {
		poly->flags |= POLY_DEGEN_FLAG | POLY_DUP_VERTS_FLAG;
	}
	return poly;
}

static PlanarPolygonObject *
Poly_new_star(PyTypeObject *type, PyObject *args, PyObject *kwargs)
{
	Py_ssize_t peak_count, i;
	double radius1, radius2, angle_step, x, y;
	PyObject *center_arg = NULL;
	double center_x = 0.0, center_y = 0.0;
	double angle = 0.0;
	planar_vec2_t *vert;
	PlanarPolygonObject *poly;

    static char *kwlist[] = {
		"peak_count", "radius1", "radius2", "center", "angle", NULL};

    if (!PyArg_ParseTupleAndKeywords(
        args, kwargs, "ndd|Od:Polygon.regular", kwlist, 
			&peak_count, &radius1, &radius2, &center_arg, &angle)) {
        return NULL;
    }
	if (peak_count < 2) {
		PyErr_SetString(PyExc_ValueError,
			"star polygon must have a minimum of 2 peaks");
		return NULL;
	}
	if (center_arg != NULL) {
		if (!PlanarVec2_Parse(center_arg, &center_x, &center_y)) {
			PyErr_SetString(PyExc_TypeError,
				"Polygon.star(): "
				"expected Vec2 object for argument center");
			return NULL;
		}
	}
	poly = Poly_alloc_new(type, peak_count * 2);
	if (poly == NULL) {
		return NULL;
	}
	angle_step = 180.0 / peak_count;
	for (i = 0, vert = poly->vert; i < peak_count; ++i, ++vert) {
		cos_sin_deg(angle, &x, &y);
		vert->x = x * radius1 + center_x;
		vert->y = y * radius1 + center_y;
		angle += angle_step;
		++vert;
		cos_sin_deg(angle, &x, &y);
		vert->x = x * radius2 + center_x;
		vert->y = y * radius2 + center_y;
		angle += angle_step;
	}
	poly->centroid.x = center_x;
	poly->centroid.y = center_y;
	x = (poly->vert[0].x + poly->vert[1].x) * 0.5 - center_x;
	y = (poly->vert[0].y + poly->vert[1].y) * 0.5 - center_y;
	if (radius1 != radius2) {
		if (radius1 < radius2) {
			poly->min_r2 = MIN(radius1 * radius1, x*x + y*y);
			poly->max_r2 = radius2 * radius2;
		} else {
			poly->min_r2 = MIN(radius2 * radius2, x*x + y*y);
			poly->max_r2 = radius1 * radius1;
		}
		poly->flags |= POLY_CONVEX_KNOWN_FLAG;
		poly->flags &= ~POLY_CONVEX_FLAG;
		poly->flags |= POLY_DUP_VERTS_FLAG * (
			radius1 == 0.0 || radius2 == 0.0);
		if ((radius1 > 0.0) == (radius2 > 0.0)) {
			poly->flags |= POLY_SIMPLE_FLAG | POLY_SIMPLE_KNOWN_FLAG
				| POLY_CENTROID_KNOWN_FLAG | POLY_RADIUS_KNOWN_FLAG 
				| POLY_DEGEN_KNOWN_FLAG;
		}
	} else {
		poly->min_r2 = x*x + y*y;
		poly->max_r2 = radius1 * radius1;
		poly->flags |= POLY_CONVEX_KNOWN_FLAG | POLY_CONVEX_FLAG
			| POLY_SIMPLE_KNOWN_FLAG | POLY_SIMPLE_FLAG 
			| POLY_CENTROID_KNOWN_FLAG | POLY_RADIUS_KNOWN_FLAG 
			| POLY_DEGEN_KNOWN_FLAG;
		if (radius1 == 0.0) {
			poly->flags |= POLY_DEGEN_FLAG | POLY_DUP_VERTS_FLAG;
		}
	}
	return poly;
}

#define DUP_FIRST_VERT(poly) {                          \
	(poly)->vert[Py_SIZE(poly)].x = (poly)->vert[0].x;  \
	(poly)->vert[Py_SIZE(poly)].y = (poly)->vert[0].y;  \
}

#define DUP_LAST_VERT(poly) {                          \
	(poly)->data[0].x = (poly)->vert[Py_SIZE(poly)-1].x;  \
	(poly)->data[0].y = (poly)->vert[Py_SIZE(poly)-1].y;  \
}

/* Comparison function for sorting of vector triples */
static int
compare_vec_triples(const void *a, const void *b)
{
	const planar_vec2_t *va = *(planar_vec2_t **)a;
	const planar_vec2_t *vb = *(planar_vec2_t **)b;
	int result, i;

	for (i = -1, result = 0; !result && i <= 1; ++i) {
		result = ((va+i)->x > (vb+i)->x) - ((va+i)->x < (vb+i)->x);
		result = result ? result : (
			(va+i)->y > (vb+i)->y) - ((va+i)->y < (vb+i)->y);
	}
	return result;
}

static int
compare_vec_triples_reverse(const void *a, const void *b)
{
	const planar_vec2_t *va = *(planar_vec2_t **)a;
	const planar_vec2_t *vb = *(planar_vec2_t **)b;
	int result, i;

	for (i = -1, result = 0; !result && i <= 1; ++i) {
		result = ((va-i)->x > (vb-i)->x) - ((va-i)->x < (vb-i)->x);
		result = result ? result : (
			(va-i)->y > (vb-i)->y) - ((va-i)->y < (vb-i)->y);
	}
	return result;
}

static int
Poly_compare_eq(PlanarPolygonObject *a, PlanarPolygonObject *b) {
	Py_ssize_t i, eq_count, ai, bi;
	planar_vec2_t *a_vert, *b_vert;
	planar_vec2_t **a_triples = NULL, **b_triples = NULL;
	const planar_vec2_t *a_end = a->vert + Py_SIZE(a);
	int is_equal;

	if (a == b) {
		return 1;
	}

	/* Test for identical verts */
	if (Py_SIZE(a) != Py_SIZE(b)) {
		return 0;
	}
	is_equal = 1;

	for (a_vert = a->vert, b_vert = b->vert; a_vert < a_end; 
		 ++a_vert, ++a_end) {
		if (VEC_NEQ(a_vert, b_vert)) {
			is_equal = 0;
			break;
		}
	}
	if (is_equal) {
		return 1;
	}

	/* Test for identical edges */
	DUP_FIRST_VERT(a);
	DUP_FIRST_VERT(b);
	DUP_LAST_VERT(a);
	DUP_LAST_VERT(b);
	a_triples = (planar_vec2_t **)PyMem_Malloc(
		sizeof(planar_vec2_t *) * Py_SIZE(a) * 2);
	if (a_triples == NULL) {
		return -1;
	}
	b_triples = a_triples + Py_SIZE(a);
	for (i = 0, a_vert = a->vert, b_vert = b->vert; i < Py_SIZE(a); ++i) {
		a_triples[i] = a_vert++;
		b_triples[i] = b_vert++;
	}
	qsort(a_triples, Py_SIZE(a), sizeof(planar_vec2_t *), compare_vec_triples);	
	qsort(b_triples, Py_SIZE(a), sizeof(planar_vec2_t *), compare_vec_triples);	
	is_equal = 1;
	for (i = 0; i < Py_SIZE(a); ++i) {
		if (VEC_NEQ(a_triples[i]-1, b_triples[i]-1)
			| VEC_NEQ(a_triples[i], b_triples[i])
		    | VEC_NEQ(a_triples[i]+1, b_triples[i]+1)) {
			is_equal = 0;
			break;
		}
	}
	if (is_equal) {
		PyMem_Free(a_triples);
		return 1;
	}
	
	/* Try comparing with reverse winding */
	qsort(b_triples, Py_SIZE(a), sizeof(planar_vec2_t *), 
		compare_vec_triples_reverse);	
	is_equal = 1;
	for (i = 0; i < Py_SIZE(a); ++i) {
		if (VEC_NEQ(a_triples[i]-1, b_triples[i]+1)
			| VEC_NEQ(a_triples[i], b_triples[i])
		    | VEC_NEQ(a_triples[i]+1, b_triples[i]-1)) {
			is_equal = 0;
			break;
		}
	}
	PyMem_Free(a_triples);
	return is_equal;
}

static PyObject *
Poly_compare(PyObject *a, PyObject *b, int op)
{
	if (PlanarPolygon_Check(a) && PlanarPolygon_Check(b)) {
		switch (op) {
			case Py_EQ:
				return Py_BOOL(Poly_compare_eq(
					(PlanarPolygonObject *)a, (PlanarPolygonObject *)b));
			case Py_NE:
				return Py_BOOL(!Poly_compare_eq(
					(PlanarPolygonObject *)a, (PlanarPolygonObject *)b));
			default:
				/* Only == and != are defined */
				RETURN_NOT_IMPLEMENTED;
		}
	} else {
		switch (op) {
			case Py_EQ:
				Py_RETURN_FALSE;
			case Py_NE:
				Py_RETURN_TRUE;
			default:
				/* Only == and != are defined */
				RETURN_NOT_IMPLEMENTED;
		}
	}
}

/* Property descriptors */

/* Calculate the polygon convexity, winding direction,
 * detecting and handling degenerate cases.
 */
static void
Poly_classify(PlanarPolygonObject *self) 
{
	int dir_changes = 0;
	int angle_sign = 0;
	Py_ssize_t count = 0;
	int same_turns = 1;
	Py_ssize_t i;
	const Py_ssize_t size = Py_SIZE(self);
	const planar_vec2_t *vert = self->vert;
	double last_dx = vert[0].x - vert[size - 1].x;
	double last_dy = vert[0].y - vert[size - 1].y;
	double dx, dy;
	double side = 0.0;
	double last_side = 0.0;
	int last_dir, this_dir;
	DUP_FIRST_VERT(self);

	for (i = 1; i <= size && !last_dx && !last_dy; ++i) {
		last_dx = vert[i].x - vert[i - 1].x;
		last_dy = vert[i].y - vert[i - 1].y;
	}

	last_dir = last_dx ? (last_dx < 0.0) - (last_dx > 0.0) 
		: (last_dy < 0.0) - (last_dy > 0.0);

	for (; i <= size && same_turns && dir_changes <= 2; ++i) {
		dx = vert[i].x - vert[i - 1].x;
		dy = vert[i].y - vert[i - 1].y;
		if (dx != 0.0 || dy != 0.0) {
			this_dir = (dx < 0.0) - (dx > 0.0) ;
			this_dir += (!this_dir) & ((dy < 0.0) - (dy > 0.0));
			dir_changes += (this_dir == -last_dir);
			last_dir = this_dir;
			side = last_dx * dy - last_dy * dx;
			if (side != 0.0) {
				same_turns = (side > 0.0) == (last_side > 0.0)
					|| last_side == 0.0;
				last_side = side;
			}
			last_dx = dx;
			last_dy = dy;
			++count;
		}
	}
	if (same_turns && dir_changes <= 2) {
		self->flags |= (POLY_CONVEX_KNOWN_FLAG | POLY_CONVEX_FLAG
			| POLY_SIMPLE_KNOWN_FLAG | POLY_SIMPLE_FLAG 
			| POLY_DUP_VERTS_KNOWN_FLAG);
		if (count < Py_SIZE(self)) {
			self->flags |= POLY_DUP_VERTS_FLAG;
		} else {
			self->flags &= ~POLY_DUP_VERTS_FLAG;
		}
	} else {
		self->flags |= POLY_CONVEX_KNOWN_FLAG;
		self->flags &= ~POLY_CONVEX_FLAG;
	}
	self->flags |= POLY_DEGEN_KNOWN_FLAG;
	if (!count || !side) {
		self->flags |= POLY_DEGEN_FLAG;
	} else {
		self->flags &= ~POLY_DEGEN_FLAG;
	}
}

/* Check the polygon for self-intersection */
static int
Poly_check_is_simple(PlanarPolygonObject *self)
{
	planar_vec2_t **points, **p, *v;
	planar_vec2_t **open = NULL;
	planar_vec2_t **o, **next_open;
	Py_ssize_t i, j;
	const Py_ssize_t size = Py_SIZE(self);
	const Py_ssize_t last_index = size - 1;
	int result = 1;

	points = (planar_vec2_t **)PyMem_Malloc(
		sizeof(planar_vec2_t *) * (size + 1));
	if (points == NULL) {
		PyErr_NoMemory();
		result = 0;
		goto finish;
	}
	DUP_FIRST_VERT(self);
	p = points;
	v = self->vert;
	for (i = 0; i <= size; ++i) {
		*(p++) = v++;
	}
	qsort(points, size + 1, sizeof(planar_vec2_t *), compare_vec_lexi);	
	open = (planar_vec2_t **)PyMem_Malloc(
		sizeof(planar_vec2_t *) * (size + 1));
	if (open == NULL) {
		PyErr_NoMemory();
		result = 0;
		goto finish;
	}

	next_open = open;
	for (i = 0, p = points; i <= size; ++i, ++p) {
		for (o = open; o < next_open; ++o) {
			if (abs(*p - *o) > 1 && abs(*p - *o) < last_index /* ignore adjacent edges */
				&& segments_intersect(*p, (*p)+1, *o, (*o)+1)) {
				self->flags |= POLY_SIMPLE_KNOWN_FLAG;
				self->flags &= ~POLY_SIMPLE_FLAG;
				goto finish;
			} else if (*p == (*o)+1) {
				/* Segment end point */ 
				--next_open;
				if (o < next_open && *o != *next_open) {
					*o = *next_open;
					--j;
				}
			}
		}
		*(next_open++) = *p;
	}
	self->flags |= POLY_SIMPLE_KNOWN_FLAG | POLY_SIMPLE_FLAG;
finish:
	if (open != NULL) {
		PyMem_Free(open);
	}
	if (points != NULL) {
		PyMem_Free(points);
	}
	return result;
}

static PyObject *
Poly_get_is_convex_known(PlanarPolygonObject *self) {
	return Py_BOOL(self->flags & POLY_CONVEX_KNOWN_FLAG);
}

static PyObject *
Poly_get_is_convex(PlanarPolygonObject *self)
{
	if (!(self->flags & POLY_CONVEX_KNOWN_FLAG)) {
		Poly_classify(self);
	}
	return Py_BOOL(self->flags & POLY_CONVEX_FLAG);
}

static PyObject *
Poly_get_is_simple_known(PlanarPolygonObject *self) {
	return Py_BOOL(self->flags & POLY_SIMPLE_KNOWN_FLAG);
}


static PyObject *
Poly_get_is_simple(PlanarPolygonObject *self)
{
	if (!(self->flags & POLY_SIMPLE_KNOWN_FLAG)) {
		if (!(self->flags & POLY_CONVEX_KNOWN_FLAG)) {
			Poly_classify(self);
		}
		if (!(self->flags & POLY_SIMPLE_KNOWN_FLAG)) {
			if (!Poly_check_is_simple(self)) {
				return NULL;
			}
		}
	}
	return Py_BOOL(self->flags & POLY_SIMPLE_FLAG);
}

static PyObject *
Poly_get_is_centroid_known(PlanarPolygonObject *self) {
	return Py_BOOL(self->flags & POLY_CENTROID_KNOWN_FLAG);
}

static PyObject *
Poly_get_centroid(PlanarPolygonObject *self)
{
	Py_ssize_t i;
	double area, total_area;
	planar_vec2_t *a, *b, *c;

	if (!(self->flags & POLY_CENTROID_KNOWN_FLAG) 
		|| !(self->flags & POLY_SIMPLE_KNOWN_FLAG)) {
		if (!(self->flags & POLY_CONVEX_KNOWN_FLAG)) {
			Poly_classify(self);
		}
		if (!(self->flags & POLY_SIMPLE_KNOWN_FLAG)) {
			if (!Poly_check_is_simple(self)) {
				return NULL;
			}
		}
		if (self->flags & POLY_SIMPLE_FLAG) {
			DUP_FIRST_VERT(self);
			total_area = 0.0;
			self->centroid.x = self->centroid.y = 0.0;
			a = self->vert;
			b = self->vert + 1;
			for (i = 2; i < Py_SIZE(self); ++i) {
				c = self->vert + i;
				area = ((b->x - a->x) * (c->y - a->y)
					- (c->x - a->x) * (b->y - a->y));
				self->centroid.x += (a->x + b->x + c->x) * area;
				self->centroid.y += (a->y + b->y + c->y) * area;
				total_area += area;
				b = c;
			}
			self->centroid.x /= 3.0 * total_area;
			self->centroid.y /= 3.0 * total_area;
		}
		self->flags |= POLY_CENTROID_KNOWN_FLAG;
	}
	if (self->flags & POLY_SIMPLE_FLAG) {
		return (PyObject *)PlanarVec2_FromStruct(&self->centroid);
	} else {
		/* No centroid for non-simple polygon */
		Py_RETURN_NONE;
	}
}

static PyGetSetDef Poly_getset[] = {
    {"is_convex_known", (getter)Poly_get_is_convex_known, NULL, 
		"True if the polygon is already known to be convex or not.", NULL},
    {"is_convex", (getter)Poly_get_is_convex, NULL, 
		"True if the polygon is convex.", NULL},
    {"is_simple_known", (getter)Poly_get_is_simple_known, NULL, 
		"True if the polygon is already known to be simple or not.", NULL},
    {"is_simple", (getter)Poly_get_is_simple, NULL, 
		"True if the polygon is simple.", NULL},
    {"is_centroid_known", (getter)Poly_get_is_centroid_known, NULL, 
		"True if the polygon's centroid has been pre-calculated and cached.",
		NULL},
    {"centroid", (getter)Poly_get_centroid, NULL, 
		"The geometric center point of the polygon. This point only exists "
        "for simple polygons. For non-simple polygons it is None. Note "
        "in concave polygons, this point may lie outside of the polygon "
		"itself.", NULL},
    {"bounding_box", (getter)PlanarBBox_fromSeq2, NULL, 
		"The bounding box of the polygon", NULL},
    {NULL}
};

/* Sequence Methods */

static PyObject *
Poly_getitem(PlanarPolygonObject *self, Py_ssize_t index)
{
    Py_ssize_t size = Py_SIZE(self);
    if (index >= 0 && index < size) {
        return (PyObject *)PlanarVec2_FromStruct(self->vert + index);
    }
    PyErr_Format(PyExc_IndexError, "index %d out of range", (int)index);
    return NULL;
}

static int
Poly_assitem(PlanarPolygonObject *self, Py_ssize_t index, PyObject *v)
{
    double x, y;
    Py_ssize_t size = Py_SIZE(self);
    if (index >= 0 && index < size) {
		if (!PlanarVec2_Parse(v, &x, &y)) {
			if (!PyErr_Occurred()) {
			PyErr_Format(PyExc_TypeError, 
				"Cannot assign %.200s into %.200s",
				Py_TYPE(v)->tp_name, Py_TYPE(self)->tp_name);
			}
			return -1;
		}
        self->vert[index].x = x;
        self->vert[index].y = y;
		self->flags = 0;
        return 0;
    }
    PyErr_Format(PyExc_IndexError, 
		"assignment index %d out of range", (int)index);
    return -1;
}

static Py_ssize_t
Poly_length(PlanarPolygonObject *self)
{
    return Py_SIZE(self);
}

static PySequenceMethods Poly_as_sequence = {
	(lenfunc)Poly_length,	/* sq_length */
	0,		/*sq_concat*/
	0,		/*sq_repeat*/
	(ssizeargfunc)Poly_getitem,		/*sq_item*/
	0,		/* sq_slice */
	(ssizeobjargproc)Poly_assitem,	/* sq_ass_item */
};

/* Methods */

static planar_vec2_t *
Poly_left_tan_convex(PlanarPolygonObject *self, planar_vec2_t *pt)
{
	planar_vec2_t *a, *b, *c;
	long down_c;
	DUP_FIRST_VERT(self);
	DUP_LAST_VERT(self);
	
	a = self->vert - 1;
	b = self->vert + Py_SIZE(self) - 1;
	if ((SIDE(pt, a + 1, a) >= 0.0) & (SIDE(pt, b - 1, b) > 0.0)) {
		return b;
	}
	while (a < b) {
		c = a + (b - a) / 2;
		down_c = SIDE(pt, c + 1, c) < 0.0;
		if ((!down_c) & (SIDE(pt, c - 1, c) > 0.0)) {
			return c;
		}
		if (SIDE(pt, a + 1, a) < 0.0) {
			if ((!down_c) | (SIDE(pt, a, c) < 0.0)) {
				b = c;
			} else {
				a = c;
			}
		} else {
			if ((down_c) | (SIDE(pt, a, c) <= 0.0)) {
				a = c;
			} else {
				b = c;
			}
		}
	}
	return a; /* should not happen */
}

static planar_vec2_t *
Poly_right_tan_convex(PlanarPolygonObject *self, planar_vec2_t *pt)
{
	planar_vec2_t *a, *b, *c;
	long down_c;
	DUP_FIRST_VERT(self);
	DUP_LAST_VERT(self);
	
	a = self->vert - 1;
	b = self->vert + Py_SIZE(self) - 1;
	if ((SIDE(pt, a + 1, a) < 0.0) & (SIDE(pt, b - 1, b) <= 0.0)) {
		return b;
	}
	while (a < b) {
		c = a + (b - a) / 2;
		down_c = SIDE(pt, c + 1, c) < 0.0;
		if ((down_c) & (SIDE(pt, c - 1, c) <= 0.0)) {
			return c;
		}
		if (SIDE(pt, a + 1, a) > 0.0) {
			if ((down_c) | (SIDE(pt, a, c) > 0.0)) {
				b = c;
			} else {
				a = c;
			}
		} else {
			if ((!down_c) | (SIDE(pt, a, c) >= 0.0)) {
				a = c;
			} else {
				b = c;
			}
		}
	}
	return a; /* should not happen */
}

static PyObject *
Poly_pt_tangents(PlanarPolygonObject *self, PyObject *point)
{
	planar_vec2_t pt;
	planar_vec2_t *left_tan = self->vert;
	planar_vec2_t *right_tan = self->vert;
	planar_vec2_t *v0 = self->vert + Py_SIZE(self) - 2;
	planar_vec2_t *v1 = v0 + 1;
	planar_vec2_t *v_end;
	double prev_turn, next_turn;

	if (!PlanarVec2_Parse(point, &pt.x, &pt.y)) {
		PyErr_SetString(PyExc_TypeError,
			"Polygon.tangents_to_point(): "
			"expected Vec2 object for argument");
		return NULL;
	}
	if (self->flags & POLY_CONVEX_FLAG) {
		left_tan = Poly_left_tan_convex(self, &pt);
		right_tan = Poly_right_tan_convex(self, &pt);
	} else {
		prev_turn = SIDE(v0, v1, &pt);
		v0 = v_end = v1;
		for (v1 = self->vert; v1 <= v_end; ++v1) {
			next_turn = SIDE(v0, v1, &pt);
			if ((prev_turn <= 0.0) & (next_turn > 0.0)) {
				if (SIDE(&pt, v0, right_tan) >= 0.0) {
					right_tan = v0;
				}
			} else if ((prev_turn > 0.0) & (next_turn <= 0.0)) {
				if (SIDE(&pt, v0, left_tan) <= 0.0) {
					left_tan = v0;
				}
			}
			v0 = v1;
			prev_turn = next_turn;
		}
	}
	return PyTuple_Pack(2, 
		PlanarVec2_FromStruct(left_tan), 
		PlanarVec2_FromStruct(right_tan));
}

static int
pnp_winding_test(PlanarPolygonObject *self, planar_vec2_t *pt)
{
	int winding_no = 0;
	planar_vec2_t *v0 = self->vert + Py_SIZE(self) - 1;
	planar_vec2_t *v_end = v0;
	planar_vec2_t *v1;
	int v1_above;
	int v0_above = (v0->y >= pt->y);
	for (v1 = self->vert; v1 <= v_end; ++v1) {
		v1_above = (v1->y >= pt->y);
		if (v0_above != v1_above) {
			if (v1_above) { /* Upward crossing */
				winding_no += (SIDE(v0, v1, pt) <= 0);
			} else {
				winding_no -= (SIDE(v0, v1, pt) >= 0);
			}
		}
		v0_above = v1_above;
		v0 = v1;
	}
	return winding_no != 0;
}

static int 
split_y_polylines(PlanarPolygonObject *self) 
{
	double min_x, max_x, min_y, max_y;	
	planar_vec2_t *v, *v_end, *p, *pl1, *pl2;
	planar_vec2_t *min, *max, *left, *right;

	self->lt_y_poly = (planar_vec2_t *)PyMem_Malloc(
		sizeof(planar_vec2_t) * (Py_SIZE(self) + 2));
	if (self->lt_y_poly == NULL) {
		return -1;
	}
	min = max = self->vert;
	min_y = max_y = self->vert[0].y;
	min_x = max_x = self->vert[0].x;
	v_end = self->vert + Py_SIZE(self) - 1;
	for (v = self->vert + 1; v <= v_end; ++v) {
		if (v->y < min_y) {
			min_y = v->y;
			min = v;
		}
		if (v->y > max_y) {
			max_y = v->y;
			max = v;
		}
		if (v->x < min_x) {
			min_x = v->x;
			left = v;
		}
		if (v->x > max_x) {
			max_x = v->x;
			right = v;
		}
	}
	if (min < max) {
		if ((min <= left && left < max) || right < min || right > max) {
			pl1 = self->lt_y_poly;
			pl2 = self->rt_y_poly = pl1 + (max - min) + 1;
		} else {
			pl2 = self->lt_y_poly;
			pl1 = self->rt_y_poly = pl2 + (Py_SIZE(self) - (max - min)) + 1;
		}
		for (v = min, p = pl1; v <= max; ++v, ++p) {
			p->x = v->x;
			p->y = v->y;
		}
		for (v = min, p = pl2; v >= self->vert; --v, ++p) {
			p->x = v->x;
			p->y = v->y;
		}
		for (v = v_end; v >= max; --v, ++p) {
			p->x = v->x;
			p->y = v->y;
		}
	} else {
		if ((min >= left && left > max) || right > min || right < max) {
			pl1 = self->lt_y_poly;
			pl2 = self->rt_y_poly = pl1 + (min - max) + 1;
		} else {
			pl2 = self->lt_y_poly;
			pl1 = self->rt_y_poly = pl2 + (Py_SIZE(self) - (min - max)) + 1;
		}
		for (v = min, p = pl1; v >= max; --v, ++p) {
			p->x = v->x;
			p->y = v->y;
		}
		for (v = min, p = pl2; v <= v_end; ++v, ++p) {
			p->x = v->x;
			p->y = v->y;
		}
		for (v = self->vert; v <= max; ++v, ++p) {
			p->x = v->x;
			p->y = v->y;
		}
	}
	return 0;
}

static int pnp_y_monotone_test(PlanarPolygonObject *self, planar_vec2_t *pt)
{
	planar_vec2_t *v, *lo, *hi;
	double pt_y = pt->y;

	if (self->lt_y_poly == NULL) {
		if (split_y_polylines(self) == -1) {
			return -1;
		}
	}
	lo = self->lt_y_poly;
	hi = self->rt_y_poly - 1;
	if ((pt_y < lo->y) | (pt_y > hi->y)) {
		return 0;
	}
	while (lo < hi) {
		v = lo + (hi - lo) / 2;
		if (pt_y < v->y) {
			hi = v;
		} else {
			lo = v + 1;
		}
	}
	if (SIDE(lo - 1, lo, pt) > 0.0) {
		/* pt too far left */
		return 0;
	}
	lo = self->rt_y_poly;
	hi = self->lt_y_poly + Py_SIZE(self) + 1;
	while (lo < hi) {
		v = lo + (hi - lo) / 2;
		if (pt_y < v->y) {
			hi = v;
		} else {
			lo = v + 1;
		}
	}
	return SIDE(lo - 1, lo, pt) > 0.0;
}

static PyObject *
Poly_contains_point(PlanarPolygonObject *self, PyObject *point)
{
	planar_vec2_t pt;
	int result;
	
	if (!PlanarVec2_Parse(point, &pt.x, &pt.y)) {
		PyErr_SetString(PyExc_TypeError,
			"Polygon.contains_point(): "
			"expected Vec2 object for argument");
		return NULL;
	}
	if (self->flags & POLY_CONVEX_FLAG && Py_SIZE(self) > 5) {
		result = pnp_y_monotone_test(self, &pt);
	} else {
		result = pnp_winding_test(self, &pt);
	}
	if (result != -1) {
		return Py_BOOL(result);
	} else {
		return PyErr_NoMemory();
	}
}

static PyObject *
Poly_pnp_y_monotone_test(PlanarPolygonObject *self, PyObject *point)
{
	planar_vec2_t pt;
	int result;
	
	if (!PlanarVec2_Parse(point, &pt.x, &pt.y)) {
		PyErr_SetString(PyExc_TypeError,
			"Polygon.contains_point(): "
			"expected Vec2 object for argument");
		return NULL;
	}
		result = pnp_y_monotone_test(self, &pt);
	if (result != -1) {
		return Py_BOOL(result);
	} else {
		return PyErr_NoMemory();
	}
}

static PyObject *
Poly_pnp_winding_test(PlanarPolygonObject *self, PyObject *point)
{
	planar_vec2_t pt;
	int result;
	
	if (!PlanarVec2_Parse(point, &pt.x, &pt.y)) {
		PyErr_SetString(PyExc_TypeError,
			"Polygon.contains_point(): "
			"expected Vec2 object for argument");
		return NULL;
	}
		result = pnp_winding_test(self, &pt);
	if (result != -1) {
		return Py_BOOL(result);
	} else {
		return PyErr_NoMemory();
	}
}


static PyMethodDef Poly_methods[] = {
    {"regular", (PyCFunction)Poly_new_regular, 
		METH_CLASS | METH_VARARGS | METH_KEYWORDS, 
		"Create a regular polygon with the specified number of vertices "
        "radius distance from the center point. Regular polygons are "
        "always convex."},
    {"star", (PyCFunction)Poly_new_star, 
		METH_CLASS | METH_VARARGS | METH_KEYWORDS, 
		"Create a circular pointed star polygon with the specified number "
        "of peaks."},
	{"tangents_to_point", (PyCFunction)Poly_pt_tangents, METH_O,
		"Given a point exterior to the polygon, return the pair of "
        "vertex points from the polygon that define the tangent lines with "
		"the specified point."},
	{"contains_point", (PyCFunction)Poly_contains_point, METH_O,
		"Return True if the specified point is inside the polygon."},
	{"_pnp_y_monotone_test", (PyCFunction)Poly_pnp_y_monotone_test, METH_O, ""},
	{"_pnp_winding_test", (PyCFunction)Poly_pnp_winding_test, METH_O, ""},
    {NULL, NULL}
};

PyDoc_STRVAR(Polygon__doc__, 
	"Arbitrary polygon represented as a list of vertices.\n\n" 
    "The individual vertices of a polygon are mutable, but the number "
    "of vertices is fixed at construction.");

PyTypeObject PlanarPolygonType = {
    PyVarObject_HEAD_INIT(NULL, 0)
	"Polygon",		/*tp_name*/
	sizeof(PlanarPolygonObject),	/*tp_basicsize*/
	sizeof(planar_vec2_t),		/*tp_itemsize*/
	/* methods */
	(destructor)Poly_dealloc, /*tp_dealloc*/
	0,			       /*tp_print*/
	0,                      /*tp_getattr*/
	0,                      /*tp_setattr*/
	0,		        /*tp_compare*/
	0, //(reprfunc)Vec2Array__repr__, /*tp_repr*/
	0, //&Vec2Array_as_number,        /*tp_as_number*/
	&Poly_as_sequence,      /*tp_as_sequence*/
	0, //&Vec2Array_as_mapping,	     /*tp_as_mapping*/
	0,	                /*tp_hash*/
	0,                      /*tp_call*/
	0, //(reprfunc)Vec2Array__repr__, /*tp_str*/
	0,                      /*tp_getattro*/
	0,                      /*tp_setattro*/
	0,                      /*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_CHECKTYPES,     /*tp_flags*/
	Polygon__doc__,       /*tp_doc*/
	0,                      /*tp_traverse*/
	0,                      /*tp_clear*/
	Poly_compare,           /*tp_richcompare*/
	0,                      /*tp_weaklistoffset*/
	0,                      /*tp_iter*/
	0,                      /*tp_iternext*/
	Poly_methods,           /*tp_methods*/
	0,                      /*tp_members*/
	Poly_getset,            /*tp_getset*/
	&PlanarSeq2Type,        /*tp_base*/
	0,                      /*tp_dict*/
	0,                      /*tp_descr_get*/
	0,                      /*tp_descr_set*/
	0,                      /*tp_dictoffset*/
	0,                      /*tp_init*/
	0,    /*tp_alloc*/
	(newfunc)Poly_new,      /*tp_new*/
	0,                      /*tp_free*/
	0,                      /*tp_is_gc*/
};

