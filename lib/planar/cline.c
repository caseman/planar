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
#include <structmember.h>
#include <float.h>
#include <string.h>
#include "planar.h"

/* Property descriptors */

static PlanarVec2Object *
Line_get_direction(PlanarLineObject *self) {
    return PlanarVec2_FromDoubles(-self->normal.y, self->normal.x);
}

static int
Line_set_direction(PlanarLineObject *self, PyObject *value, void *closure)
{
    double dx, dy, L;

    if (value == NULL) {
        PyErr_SetString(PyExc_TypeError, "Cannot delete direction attribute");
        return -1;
    }
    if (!PlanarVec2_Parse(value, &dx, &dy)) {
        PyErr_SetString(PyExc_TypeError, "Expected Vec2 for direction");
        return -1;
    }
    L = sqrt(dx*dx + dy*dy);
    if (L < PLANAR_EPSILON) {
        PyErr_SetString(PyExc_ValueError, "Direction vector must not be null");
        return -1;
    }
    self->normal.x = dy / L;
    self->normal.y = -dx / L;
    return 0;
}

static PlanarVec2Object *
Line_get_normal(PlanarLineObject *self) {
    return PlanarVec2_FromStruct(&self->normal);
}

static int
Line_set_normal(PlanarLineObject *self, PyObject *value, void *closure)
{
    double nx, ny, L;

    if (value == NULL) {
        PyErr_SetString(PyExc_TypeError, "Cannot delete normal attribute");
        return -1;
    }
    if (!PlanarVec2_Parse(value, &nx, &ny)) {
        PyErr_SetString(PyExc_TypeError, "Expected Vec2 for normal");
        return -1;
    }
    L = sqrt(nx*nx + ny*ny);
    if (L < PLANAR_EPSILON) {
        PyErr_SetString(PyExc_ValueError, "Normal vector must not be null");
        return -1;
    }
    self->normal.x = nx / L;
    self->normal.y = ny / L;
    return 0;
}

static PlanarSeq2Object *
Line_get_points(PlanarLineObject *self) {
    PlanarSeq2Object *seq;
    double sx, sy, dx, dy;

    seq = Seq2_New(&PlanarSeq2Type, 2);
    if (seq != NULL) {
        seq->vec[0].x = sx = self->normal.x * self->offset;
        seq->vec[0].y = sy = self->normal.y * self->offset;
        seq->vec[1].x = sx + self->normal.y;
        seq->vec[1].y = sy + -self->normal.x;
    }
    return seq;
}

static int
Line_set_offset(PlanarLineObject *self, PyObject *value)
{
    value = PyObject_ToFloat(value);
    if (value == NULL) {
        return -1;
    }
    self->offset = PyFloat_AS_DOUBLE(value);
    Py_DECREF(value);
    return 0;
}

static PyMemberDef Line_members[] = {
    {"offset", T_DOUBLE, offsetof(PlanarLineObject, offset), 0,
        "Direction from the origin to the line."},
    {NULL}
};

static PyGetSetDef Line_getset[] = {
    {"direction", (getter)Line_get_direction, (setter)Line_set_direction, 
        "Direction of the line as a unit vector.", NULL},
    {"normal", (getter)Line_get_normal, (setter)Line_set_normal, 
        "Normal unit vector perpendicular to the line.", NULL},
    {"points", (getter)Line_get_points, NULL, 
        "Two distinct points along the line.", NULL},
    {NULL}
};

/* Methods */

static int
Line_init(PlanarLineObject *self, PyObject *args)
{
    double px, py;

    assert(PlanarLine_Check(self));
    if (PyTuple_GET_SIZE(args) != 2) {
        PyErr_SetString(PyExc_TypeError, "Line: wrong number of arguments");
        return -1;
    }
    if (!PlanarVec2_Parse(PyTuple_GET_ITEM(args, 0), &px, &py)) {
        return -1;
    }
    if (Line_set_direction(self, PyTuple_GET_ITEM(args, 1), NULL) == -1) {
        return -1;
    }
    self->offset = px * self->normal.x + py * self->normal.y;
    return 0;
}

static PyObject *
Line_repr(PlanarLineObject *self)
{
    char buf[255];

    buf[0] = 0; /* paranoid */
    PyOS_snprintf(buf, 255, "Line((%g, %g), (%g, %g))",
        self->normal.x * self->offset, self->normal.y * self->offset, 
        -self->normal.y, self->normal.x);
    return PyUnicode_FromString(buf);
}

static PlanarLineObject *
Line_new_from_points(PyTypeObject *type, PyObject *points) 
{
    PlanarLineObject *line;
    planar_vec2_t *vec, p1, p2;
    Py_ssize_t size;
    int i;
    double x, y, dx, dy, px, py, d, L;

    assert(PyType_IsSubtype(type, &PlanarLineType));
    line = (PlanarLineObject *)type->tp_alloc(type, 0);
    if (line == NULL) {
        return NULL;
    }

    if (PlanarSeq2_Check(points)) {
        /* Optimized code path for Seq2 objects */
        if (Py_SIZE(points) < 2) {
            goto tooShort;
        }
        vec = ((PlanarSeq2Object *)points)->vec;
        x = vec[0].x;
        y = vec[0].y;
        for (i = 1; i < Py_SIZE(points); ++i) {
            dx = vec[i].x - x;
            dy = vec[i].y - y;
            L = dx*dx + dy*dy;
            if (L > PLANAR_EPSILON2) break;
        }
        if (L < PLANAR_EPSILON2) goto tooShort;
        while (++i < size) {
            d = vec[i].x * -dy + vec[i].y * dx;
            if ((d < -PLANAR_EPSILON) | (d > PLANAR_EPSILON)) {
                goto notCollinear;
            }
        }
    } else {
        points = PySequence_Fast(points, "expected iterable of Vec2 objects");
        if (points == NULL) {
            return NULL;
        }
        size = PySequence_Fast_GET_SIZE(points);
        if (Py_SIZE(points) < 2) {
            Py_DECREF(points);
            goto tooShort;
        }
        if (!PlanarVec2_Parse(PySequence_Fast_GET_ITEM(points, 0), &x, &y)) {
            Py_DECREF(points);
            goto wrongType;
        }
        for (i = 1; i < size; ++i) {
            if (!PlanarVec2_Parse(
                PySequence_Fast_GET_ITEM(points, i), &dx, &dy)) {
                Py_DECREF(points);
                goto wrongType;
            }
            dx -= x;
            dy -= y;
            L = dx*dx + dy*dy;
            if (L > PLANAR_EPSILON2) break;
        }
        while (++i < size) {
            if (!PlanarVec2_Parse(
                PySequence_Fast_GET_ITEM(points, i), &px, &py)) {
                Py_DECREF(points);
                goto wrongType;
            }
            d = px * dy + py * -dx;
            if ((d < -PLANAR_EPSILON) | (d > PLANAR_EPSILON)) {
                Py_DECREF(points);
                goto notCollinear;
            }
        }
        Py_DECREF(points);
        if (L < PLANAR_EPSILON2) goto tooShort;
    }
    L = sqrt(L);
    line->normal.x = dy / L;
    line->normal.y = -dx / L;
    line->offset = line->normal.x * x + line->normal.y * y;
    return line;

wrongType:
    PyErr_SetString(PyExc_TypeError, "expected iterable of Vec2 objects");
    return NULL;
tooShort:
    PyErr_SetString(PyExc_ValueError,
        "Expected iterable of 2 or more distinct points");
    return NULL;
notCollinear:
    PyErr_SetString(PyExc_ValueError, "All points provided must be collinear");
    return NULL;
}

static PlanarLineObject *
Line_new_from_normal(PyTypeObject *type, PyObject *args)
{
    PlanarLineObject *line;
    planar_vec2_t *vec, p1, p2;
    Py_ssize_t size;
    int i;
    double x, y, dx, dy, L;

    assert(PyType_IsSubtype(type, &PlanarLineType));
    if (PyTuple_GET_SIZE(args) != 2) {
        PyErr_SetString(PyExc_TypeError, 
            "Line.from_normal: wrong number of arguments");
        return NULL;
    }
    line = (PlanarLineObject *)type->tp_alloc(type, 0);
    if (line != NULL) {
        if (Line_set_normal(line, PyTuple_GET_ITEM(args, 0), NULL) == -1) {
            return NULL;
        }
        if (Line_set_offset(line, PyTuple_GET_ITEM(args, 1)) == -1) {
            return NULL;
        }
    }
    return line;
}

static PyObject *
Line_distance_to(PlanarLineObject *self, PyObject *pt)
{
    double px, py;

    if (!PlanarVec2_Parse(pt, &px, &py)) {
        return NULL;
    }
    return PyFloat_FromDouble(
        self->normal.x * px + self->normal.y * py - self->offset);
}

static PyObject *
Line_point_left(PlanarLineObject *self, PyObject *pt)
{
    double px, py, d;

    if (!PlanarVec2_Parse(pt, &px, &py)) {
        return NULL;
    }
    d = self->normal.x * px + self->normal.y * py - self->offset;
    return Py_BOOL(d <= -PLANAR_EPSILON);
}

static PyObject *
Line_point_right(PlanarLineObject *self, PyObject *pt)
{
    double px, py, d;

    if (!PlanarVec2_Parse(pt, &px, &py)) {
        return NULL;
    }
    d = self->normal.x * px + self->normal.y * py - self->offset;
    return Py_BOOL(d >= PLANAR_EPSILON);
}

static PyObject *
Line_contains_point(PlanarLineObject *self, PyObject *pt)
{
    double px, py, d;

    if (!PlanarVec2_Parse(pt, &px, &py)) {
        return NULL;
    }
    d = self->normal.x * px + self->normal.y * py - self->offset;
    return Py_BOOL((d < PLANAR_EPSILON) & (d > -PLANAR_EPSILON));
}

static PyMethodDef Line_methods[] = {
    {"from_points", (PyCFunction)Line_new_from_points, METH_CLASS | METH_O, 
        "Create a line from two or more collinear points."},
    {"from_normal", (PyCFunction)Line_new_from_normal, 
        METH_CLASS | METH_VARARGS, 
        "Create a line given a normal vector perpendicular to it, at the "
        "specified distance from the origin."},
    {"distance_to", (PyCFunction)Line_distance_to, METH_O,
        "Return the signed distance from the line to the specified point."},
    {"point_left", (PyCFunction)Line_point_left, METH_O,
        "Return True if the specified point is in the half plane "
        "to the left of the line."},
    {"point_right", (PyCFunction)Line_point_right, METH_O,
        "Return True if the specified point is in the half plane "
        "to the right of the line."},
    {"contains_point", (PyCFunction)Line_contains_point, METH_O,
        "Return True if the specified point is on the line."},
    {NULL, NULL}
};

/* Arithmetic Operations */

static PyNumberMethods Line_as_number = {
    0,       /* binaryfunc nb_add */
    0,       /* binaryfunc nb_subtract */
    0,       /* binaryfunc nb_multiply */
};

PyDoc_STRVAR(Line_doc, 
    "Infinite directed line.\n\n"
    "Line(point, direction)"
);

PyTypeObject PlanarLineType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "planar.Line",     /* tp_name */
    sizeof(PlanarLineObject), /* tp_basicsize */
    0,                    /* tp_itemsize */
    0,                       /* tp_dealloc */
    0,                    /* tp_print */
    0,                    /* tp_getattr */
    0,                    /* tp_setattr */
    0,                    /* reserved */
    (reprfunc)Line_repr,  /* tp_repr */
    &Line_as_number,      /* tp_as_number */
    0,                    /* tp_as_sequence */
    0,                    /* tp_as_mapping */
    0,                    /* tp_hash */
    0,                    /* tp_call */
    (reprfunc)Line_repr,  /* tp_str */
    0,                    /* tp_getattro */
    0,                    /* tp_setattro */
    0,                    /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_CHECKTYPES,   /* tp_flags */
    Line_doc,             /* tp_doc */
    0,                    /* tp_traverse */
    0,                    /* tp_clear */
    0, //Line_compare,         /* tp_richcompare */
    0,                    /* tp_weaklistoffset */
    0,                    /* tp_iter */
    0,                    /* tp_iternext */
    Line_methods,         /* tp_methods */
    Line_members,         /* tp_members */
    Line_getset,          /* tp_getset */
    0,                    /* tp_base */
    0,                    /* tp_dict */
    0,                    /* tp_descr_get */
    0,                    /* tp_descr_set */
    0,                    /* tp_dictoffset */
    (initproc)Line_init,  /* tp_init */
    0,                    /* tp_alloc */
    0,                    /* tp_new */
    0,                    /* tp_free */
};

