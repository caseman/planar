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
Poly_new(PyTypeObject *type, PyObject *args, PyObject *kwargs)
{
	PyObject *verts_arg, *is_convex_arg = NULL, *is_simple_arg = NULL;
	PyObject *verts_seq = NULL;
	PlanarPolygonObject *poly = NULL;
	Py_ssize_t size, i;

    static char *kwlist[] = {"vertices", "is_convex", "is_simple", NULL};

    assert(PlanarPolygon_Check(self));
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
	if (size < 3) {
		PyErr_Format(PyExc_ValueError,
			"Polygon(): minimum of 3 vertices required");
		goto error;
	}
	/* Allocate one extra vert to duplicate the first to
	 * simplify operations */
	poly = (PlanarPolygonObject *)type->tp_alloc(type, size + 1);
	Py_SIZE(poly) = size;
	if (poly == NULL) {
		goto error;
	}
	poly->vert = poly->data;
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
    Py_TYPE(self)->tp_free((PyObject *)self);
}

#define DUP_FIRST_VERT(poly) {                          \
	(poly)->vert[Py_SIZE(poly)].x = (poly)->vert[0].x;  \
	(poly)->vert[Py_SIZE(poly)].y = (poly)->vert[0].y;  \
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
	0, //Seq2_compare,           /*tp_richcompare*/
	0,                      /*tp_weaklistoffset*/
	0,                      /*tp_iter*/
	0,                      /*tp_iternext*/
	0, //Vec2Array_methods,           /*tp_methods*/
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

