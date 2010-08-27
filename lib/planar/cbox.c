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

#define BBOX_FREE_MAX 200
static PyObject *bbox_free_list = NULL;
static int bbox_free_size = 0;

static int
BBox_init_from_points(PlanarBBoxObject *self, PyObject *points) 
{
    planar_vec2_t *vec;
    Py_ssize_t size;
    int i;
    double x, y;

    if (PlanarSeq2_Check(points)) {
        /* Optimized code path for Seq2 objects */
        if (Py_SIZE(points) < 1) {
            goto tooShort;
        }
        vec = ((PlanarSeq2Object *)points)->vec;
        self->max.x = self->min.x = vec->x;
        self->max.y = self->min.y = vec->y;
        for (i = 1; i < Py_SIZE(points); ++i) {
            ++vec;
            if (vec->x > self->max.x) {
                self->max.x = vec->x;
            } else if (vec->x < self->min.x) {
                self->min.x = vec->x;
            }
            if (vec->y > self->max.y) {
                self->max.y = vec->y;
            } else if (vec->y < self->min.y) {
                self->min.y = vec->y;
            }
        }
    } else {
        points = PySequence_Fast(points, "expected iterable of Vec2 objects");
		if (points == NULL) {
			return -1;
		}
		size = PySequence_Fast_GET_SIZE(points);
        if (Py_SIZE(points) < 1) {
            Py_DECREF(points);
            goto tooShort;
        }
        if (!PlanarVec2_Parse(PySequence_Fast_GET_ITEM(points, 0), &x, &y)) {
            Py_DECREF(points);
            goto wrongType;
        }
        self->max.x = self->min.x = x;
        self->max.y = self->min.y = y;
        for (i = 1; i < size; ++i) {
			if (!PlanarVec2_Parse(PySequence_Fast_GET_ITEM(points, i), 
				&x, &y)) {
                Py_DECREF(points);
                goto wrongType;
			}
            if (x > self->max.x) {
                self->max.x = x;
            } else if (x < self->min.x) {
                self->min.x = x;
            }
            if (y > self->max.y) {
                self->max.y = y;
            } else if (y < self->min.y) {
                self->min.y = y;
            }
		}
		Py_DECREF(points);
    }
    return 0;

wrongType:
    PyErr_SetString(PyExc_TypeError, "expected iterable of Vec2 objects");
    return -1;
tooShort:
    PyErr_SetString(PyExc_ValueError,
        "Cannot construct a BoundingBox without at least one point");
    return -1;
}

static int
BBox_init(PlanarBBoxObject *self, PyObject *args)
{
    assert(PlanarBBox_Check(self));
    if (PyTuple_GET_SIZE(args) != 1) {
        PyErr_SetString(PyExc_TypeError, 
            "BoundingBox: wrong number of arguments");
        return -1;
    }
    return BBox_init_from_points(self, PyTuple_GET_ITEM(args, 0));
}

static PyObject *
BBox_alloc(PyTypeObject *type, Py_ssize_t nitems)
{
    int i;
    PlanarBBoxObject *box;

    assert(PyType_IsSubtype(type, &PlanarBBoxType));
    if (bbox_free_list != NULL) {
        box = (PlanarBBoxObject *)bbox_free_list;
        Py_INCREF(box);
        bbox_free_list = box->next_free;
        --bbox_free_size;
		return (PyObject *)box;
    } else {
        return PyType_GenericAlloc(type, nitems);
    }
}

static void
BBox_dealloc(PlanarBBoxObject *self)
{
    if (PlanarBBox_CheckExact(self) && bbox_free_size < BBOX_FREE_MAX) {
        self->next_free = bbox_free_list;
        bbox_free_list = (PyObject *)self;
        ++bbox_free_size;
    } else {
        Py_TYPE(self)->tp_free((PyObject *)self);
    }
}

/* Property descriptors */

static PlanarVec2Object *
BBox_get_max_point(PlanarBBoxObject *self) {
    return PlanarVec2_FromStruct(&self->max);
}

static PlanarVec2Object *
BBox_get_min_point(PlanarBBoxObject *self) {
    return PlanarVec2_FromStruct(&self->min);
}

static PlanarVec2Object *
BBox_get_center(PlanarBBoxObject *self) {
    return PlanarVec2_FromDoubles(
        (self->min.x + self->max.x) / 2.0,
        (self->min.y + self->max.y) / 2.0);
}

static PyObject *
BBox_get_width(PlanarBBoxObject *self) {
    return PyFloat_FromDouble(self->max.x - self->min.x);    
}

static PyObject *
BBox_get_height(PlanarBBoxObject *self) {
    return PyFloat_FromDouble(self->max.y - self->min.y);    
}

static PyObject *
BBox_get_is_empty(PlanarBBoxObject *self) {
    PyObject *r;

    if (self->max.x == self->min.x || self->max.y == self->min.y) {
        r = Py_True;
    } else {
        r = Py_False;
    }
    Py_INCREF(r);
    return r;
}

static PlanarBBoxObject *
BBox_get_bounding_box(PlanarBBoxObject *self) {
    Py_INCREF(self);
    return self;
}

static PyGetSetDef BBox_getset[] = {
    {"max_point", (getter)BBox_get_max_point, NULL, 
        "The maximum corner point for the shape. "
        "This is the corner with the largest x and y value.", NULL},
    {"min_point", (getter)BBox_get_min_point, NULL, 
        "The minimum corner point for the shape. "
        "This is the corner with the smallest x and y value.", NULL},
    {"center", (getter)BBox_get_center, NULL, 
        "The center point of the box.", NULL},
    {"width", (getter)BBox_get_width, NULL, 
        "The width of the box.", NULL},
    {"height", (getter)BBox_get_height, NULL, 
        "The height of the box.", NULL},
    {"is_empty", (getter)BBox_get_is_empty, NULL, 
        "True if the box has zero area.", NULL},
    {"bounding_box", (getter)BBox_get_bounding_box, NULL, 
        "The bounding box for this shape. "
        "For a BoundingBox instance, this is always itself.", NULL},
    {NULL}
};

PyDoc_STRVAR(BBox_doc, 
    "An axis-aligned immutable rectangular shape.\n\n"
    "BoundingBox(points)"
);

PyTypeObject PlanarBBoxType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "planar.BoundingBox",     /* tp_name */
    sizeof(PlanarBBoxObject), /* tp_basicsize */
    0,                    /* tp_itemsize */
    (destructor)BBox_dealloc, /* tp_dealloc */
    0,                    /* tp_print */
    0,                    /* tp_getattr */
    0,                    /* tp_setattr */
    0,                    /* reserved */
    0, // (reprfunc)BBox_repr,  /* tp_repr */
    0,                    /* tp_as_number */
    0,                    /* tp_as_sequence */
    0,                    /* tp_as_mapping */
    0,                    /* tp_hash */
    0,                    /* tp_call */
    0, //(reprfunc)BBox_str,   /* tp_str */
    0,                    /* tp_getattro */
    0,                    /* tp_setattro */
    0,                    /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_CHECKTYPES,   /* tp_flags */
    BBox_doc,             /* tp_doc */
    0,                    /* tp_traverse */
    0,                    /* tp_clear */
    0, //BBox_compare,         /* tp_richcompare */
    0,                    /* tp_weaklistoffset */
    0,                    /* tp_iter */
    0,                    /* tp_iternext */
    0, //BBox_methods,                    /* tp_methods */
    0,                    /* tp_members */
    BBox_getset,                    /* tp_getset */
    0,                    /* tp_base */
    0,                    /* tp_dict */
    0,                    /* tp_descr_get */
    0,                    /* tp_descr_set */
    0,                    /* tp_dictoffset */
    (initproc)BBox_init,  /* tp_init */
    BBox_alloc,           /* tp_alloc */
    0,                    /* tp_new */
    0,                    /* tp_free */
};

