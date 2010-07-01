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

#define VEC2_FREE_MAX 1000
static PyObject *vec2_free_list = NULL;
static int vec2_free_size = 0;

static PlanarVec2Object *
Vec2_result(PlanarVec2Object *self, double x, double y)
{
    PlanarVec2Object *v;

    assert(PlanarVec2_Check(self));
    v = (PlanarVec2Object *)PlanarVec2Type.tp_alloc(Py_TYPE(self), 0);
    if (v == NULL) {
        return NULL;
    }
    v->x = x;
    v->y = y;
    return v;
}

static int
Vec2_init(PlanarVec2Object *self, PyObject *args)
{
    PyObject *xarg;
    PyObject *yarg;

    assert(PlanarVec2_Check(self));
    if (PyTuple_GET_SIZE(args) != 2) {
        PyErr_SetString(PyExc_TypeError, 
            "Vec2: wrong number of arguments");
        return -1;
    }
    xarg = PyObject_ToFloat(PyTuple_GET_ITEM(args, 0));
    yarg = PyObject_ToFloat(PyTuple_GET_ITEM(args, 1));
    if (xarg == NULL || yarg == NULL) {
        Py_XDECREF(xarg);
        Py_XDECREF(yarg);
        return -1;
    }

    self->x = PyFloat_AS_DOUBLE(xarg);
    self->y = PyFloat_AS_DOUBLE(yarg);
    Py_DECREF(xarg);
    Py_DECREF(yarg);
    return 0;
}

static PyObject *
Vec2_alloc(PyTypeObject *type, Py_ssize_t nitems)
{
    PlanarVec2Object *v;

    assert(PyType_IsSubtype(type, &PlanarVec2Type));
    if (vec2_free_list != NULL) {
        v = (PlanarVec2Object *)vec2_free_list;
        Py_INCREF(v);
        vec2_free_list = v->next_free;
        --vec2_free_size;
        v->x = v->y = 0.0;
        return (PyObject *)v;
    } else {
        PyObject *p = PyType_GenericAlloc(type, nitems);
        return p;
    }
}

static void
Vec2_dealloc(PlanarVec2Object *self)
{
    if (PlanarVec2_CheckExact(self) && vec2_free_size < VEC2_FREE_MAX) {
        self->next_free = vec2_free_list;
        vec2_free_list = (PyObject *)self;
        ++vec2_free_size;
    } else {
        Py_TYPE(self)->tp_free((PyObject *)self);
    }
}

static PyObject *
Vec2_compare(PyObject *a, PyObject *b, int op)
{
    double ax, bx, ay, by;
    int result = 0;

    if (PlanarVec2_Parse(a, &ax, &ay) && PlanarVec2_Parse(b, &bx, &by)) {
        switch (op) {
            case Py_EQ:
                result = ax == bx && ay == by;
                break;
            case Py_NE:
                result = ax != bx || ay != by;
                break;
            case Py_GT:
                result = (ax*ax + ay*ay) > (bx*bx + by*by);
                break;
            case Py_LT:
                result = (ax*ax + ay*ay) < (bx*bx + by*by);
                break;
            case Py_GE:
                result = (ax*ax + ay*ay) >= (bx*bx + by*by);
                break;
            case Py_LE:
                result = (ax*ax + ay*ay) <= (bx*bx + by*by);
                break;
            default:
                RETURN_NOT_IMPLEMENTED;
        }
	if (result) {
	    Py_RETURN_TRUE;
	} else {
	    Py_RETURN_FALSE;
	}
    } else {
        /* We can't parse one or both operands */
        if (PyErr_Occurred() && PyErr_ExceptionMatches(PyExc_MemoryError)) {
            /* Don't mask memory errors */
            return NULL;
        }
        PyErr_Clear();
        switch (op) {
            case Py_EQ:
                Py_RETURN_FALSE;
            case Py_NE:
                Py_RETURN_TRUE;
            default:
                /* Other comparisons are undefined */
                RETURN_NOT_IMPLEMENTED;
        }
    }
}

static long
Vec2_hash(PlanarVec2Object *self) 
{
    long hash;

    hash = (hash_double(self->x) + LONG_MAX/2) ^ hash_double(self->y);
    return (hash != -1) ? hash : -2;
}    

/* Property descriptors */

static PyObject *
Vec2_get_x(PlanarVec2Object *self) {
    return PyFloat_FromDouble(self->x);
}

static PyObject *
Vec2_get_y(PlanarVec2Object *self) {
    return PyFloat_FromDouble(self->y);
}

static PyObject *
Vec2_get_length(PlanarVec2Object *self) {
    return PyFloat_FromDouble(sqrt(self->y * self->y + self->x * self->x));
}

static PyObject *
Vec2_get_length2(PlanarVec2Object *self) {
    return PyFloat_FromDouble(self->y * self->y + self->x * self->x);
}

static PyObject *
Vec2_get_angle(PlanarVec2Object *self) {
    return PyFloat_FromDouble(degrees(atan2(self->y, self->x)));
}

static PyObject *
Vec2_get_is_null(PlanarVec2Object *self)
{
    if (self->y * self->y + self->x * self->x < PLANAR_EPSILON2) {
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
}

static PyGetSetDef Vec2_getset[] = {
    {"x", (getter)Vec2_get_x, NULL, "The horizontal coordinate.", NULL},
    {"y", (getter)Vec2_get_y, NULL, "The vertical coordinate.", NULL},
    {"length", (getter)Vec2_get_length, NULL, 
        "The length or scalar magnitude of the vector.", NULL},
    {"length2", (getter)Vec2_get_length2, NULL, 
        "The square of the length of the vector.", NULL},
    {"angle", (getter)Vec2_get_angle, NULL, 
        "The angle the vector makes to the positive x axis in the range"
        " (-180, 180]"},
    {"is_null", (getter)Vec2_get_is_null, NULL, 
        "Flag indicating if the vector is effectively zero-length."},
    {NULL}
};

/* Methods */

static PyObject *
Vec2_new_polar(PyTypeObject *type, PyObject *args, PyObject *kwargs)
{
    PyObject *angle_arg;
    PyObject *length_arg;
    PlanarVec2Object *v;
    int arg_count;
    double angle;
    double length = 1.0;

    static char *kwlist[] = {"angle", "length", NULL};

    assert(PyType_IsSubtype(type, &PlanarVec2Type));
    if (kwargs == NULL) {
        /* No kwargs, do fast manual arg handling */
        arg_count = PyTuple_GET_SIZE(args);
        if (arg_count != 1 && arg_count != 2) {
            PyErr_SetString(PyExc_TypeError, 
                "Vec2.polar(): wrong number of arguments");
            return NULL;
        }
        angle_arg = PyObject_ToFloat(PyTuple_GET_ITEM(args, 0));
        if (angle_arg == NULL) {
            return NULL;
        }
        angle = PyFloat_AS_DOUBLE(angle_arg);
        Py_DECREF(angle_arg);
        if (arg_count == 2) {
            length_arg = PyObject_ToFloat(PyTuple_GET_ITEM(args, 1));
            if (length_arg == NULL) {
                return NULL;
            }
            length = PyFloat_AS_DOUBLE(length_arg);
            Py_DECREF(length_arg);
        }
    } else if (!PyArg_ParseTupleAndKeywords(
        args, kwargs, "d|d:Vec2.polar", kwlist, &angle, &length)) {
        return NULL;
    }

    v = (PlanarVec2Object *)type->tp_alloc(type, 0);
    if (v != NULL) {
        angle = radians(angle);
        v->x = cos(angle) * length;
        v->y = sin(angle) * length;
    }
    return (PyObject *)v;
}

static PyObject *
Vec2_repr(PlanarVec2Object *self)
{
    char buf[255];
    buf[0] = 0; /* paranoid */
    PyOS_snprintf(buf, 255, "Vec2(%lg, %lg)", self->x, self->y);
    return PyUnicode_FromString(buf);
}

static PyObject *
Vec2_str(PlanarVec2Object *self)
{
    char buf[255];
    buf[0] = 0; /* paranoid */
    PyOS_snprintf(buf, 255, "Vec2(%.2f, %.2f)", self->x, self->y);
    return PyUnicode_FromString(buf);
}

static PyObject *
Vec2_almost_equals(PlanarVec2Object *self, PyObject *other)
{
    double ox, oy, dx, dy;

    assert(PlanarVec2_Check(self));
    if (PlanarVec2_Parse(other, &ox, &oy)) {
        dx = self->x - ox;
        dy = self->y - oy;
        if (dx*dx + dy*dy <= PLANAR_EPSILON2) {
            Py_RETURN_TRUE;
        } else {
            Py_RETURN_FALSE;
        }
    } else {
        CONVERSION_ERROR();
    }
}

static PyObject *
Vec2_angle_to(PlanarVec2Object *self, PyObject *other)
{
    double ox, oy;

    assert(PlanarVec2_Check(self));
    if (PlanarVec2_Parse(other, &ox, &oy)) {
        return PyFloat_FromDouble(
            degrees(atan2(oy, ox) - atan2(self->y, self->x)));
    } else {
        CONVERSION_ERROR();
    }
}

static PyObject *
Vec2_distance_to(PlanarVec2Object *self, PyObject *other)
{
    double ox, oy, dx, dy;

    assert(PlanarVec2_Check(self));
    if (PlanarVec2_Parse(other, &ox, &oy)) {
        dx = self->x - ox;
        dy = self->y - oy;
        return PyFloat_FromDouble(sqrt(dx*dx + dy*dy));
    } else {
        CONVERSION_ERROR();
    }
}

static PyObject *
Vec2_dot(PlanarVec2Object *self, PyObject *other)
{
    double ox, oy;

    assert(PlanarVec2_Check(self));
    if (PlanarVec2_Parse(other, &ox, &oy)) {
        return PyFloat_FromDouble(self->x * ox + self->y * oy);
    } else {
        CONVERSION_ERROR();
    }
}

static PyObject *
Vec2_cross(PlanarVec2Object *self, PyObject *other)
{
    double ox, oy;

    assert(PlanarVec2_Check(self));
    if (PlanarVec2_Parse(other, &ox, &oy)) {
        return PyFloat_FromDouble(self->x * oy - self->y * ox);
    } else {
        CONVERSION_ERROR();
    }
}

static PlanarVec2Object *
Vec2_rotated(PlanarVec2Object *self, PyObject *angle_arg)
{
    double angle, sa, ca;

    assert(PlanarVec2_Check(self));
    angle_arg = PyObject_ToFloat(angle_arg);
    if (angle_arg == NULL) {
        return NULL;
    }
    angle = radians(PyFloat_AS_DOUBLE(angle_arg));
    sa = sin(angle);
    ca = cos(angle);
    return Vec2_result(self, 
        self->x * ca - self->y * sa, self->x * sa + self->y * ca);
}

static PlanarVec2Object *
Vec2_scaled_to(PlanarVec2Object *self, PyObject *length)
{
    double L, s;

    assert(PlanarVec2_Check(self));
    length = PyObject_ToFloat(length);
    if (length == NULL) {
        return NULL;
    }
    L = self->x * self->x + self->y * self->y;
    if (L >= PLANAR_EPSILON2) {
        s = PyFloat_AS_DOUBLE(length) / sqrt(L);
        Py_DECREF(length);
        return Vec2_result(self, self->x * s, self->y * s);
    } else {
        return Vec2_result(self, 0.0, 0.0);
    }
}

static PlanarVec2Object *
Vec2_project(PlanarVec2Object *self, PyObject *other)
{
    double ox, oy, L, s;

    assert(PlanarVec2_Check(self));
    if (PlanarVec2_Parse(other, &ox, &oy)) {
        L = self->x * self->x + self->y * self->y;
        if (L >= PLANAR_EPSILON2) {
            s = (self->x * ox + self->y * oy) / L;
            return Vec2_result(self, self->x * s, self->y * s);
        } else {
            return Vec2_result(self, 0.0, 0.0);
        }
    } else {
        CONVERSION_ERROR();
    }
}

static PlanarVec2Object *
Vec2_reflect(PlanarVec2Object *self, PyObject *other)
{
    double ox, oy, L, s;

    assert(PlanarVec2_Check(self));
    if (PlanarVec2_Parse(other, &ox, &oy)) {
        L = ox * ox + oy * oy;
        if (L >= PLANAR_EPSILON2) {
            s = 2 * (self->x * ox + self->y * oy) / L;
            return Vec2_result(self, ox * s - self->x, oy * s - self->y);
        } else {
            return Vec2_result(self, 0.0, 0.0);
        }
    } else {
        CONVERSION_ERROR();
    }
}

static PlanarVec2Object *
Vec2_clamped(PlanarVec2Object *self, PyObject *args, PyObject *kwargs)
{
    double min = 0.0;
    double max = DBL_MAX;
    double L, CL;

    static char *kwlist[] = {"min_length", "max_length", NULL};

    assert(PlanarVec2_Check(self));
    if (!PyArg_ParseTupleAndKeywords(
        args, kwargs, "|dd:Vec2.clamped", kwlist, &min, &max)) {
        return NULL;
    }
    if (min > max) {
        PyErr_SetString(PyExc_ValueError, 
            "Vec2.clamped: expected min_length <= max_length");
        return NULL;
    }

    L = sqrt(self->y * self->y + self->x * self->x);
    CL = (L < min) ? min : L;
    CL = (CL > max) ? max : CL;

    if (L > PLANAR_EPSILON) {
        return Vec2_result(self, 
            self->x * (CL / L), self->y * (CL / L));
    } else {
        return Vec2_result(self, 0.0, 0.0);
    }
}

static PlanarVec2Object *
Vec2_lerp(PlanarVec2Object *self, PyObject *args)
{
    PyObject *other;
    double v, ox, oy;

    assert(PlanarVec2_Check(self));
    if (!PyArg_ParseTuple(args, "Od", &other, &v)) {
        return NULL;
    }
    if (!PlanarVec2_Parse(other, &ox, &oy)) {
        return NULL;
    }
    return Vec2_result(self, 
        self->x * (1.0 - v) + ox * v, 
        self->y * (1.0 - v) + oy * v);
}

static PlanarVec2Object *
Vec2_normalized(PlanarVec2Object *self)
{
    double length;

    assert(PlanarVec2_Check(self));
    length = sqrt(self->y * self->y + self->x * self->x);
    if (length > PLANAR_EPSILON) {
        return Vec2_result(self, self->x / length, self->y / length);
    } else {
        return Vec2_result(self, 0.0, 0.0);
    }
}

static PlanarVec2Object *
Vec2_perpendicular(PlanarVec2Object *self)
{
    assert(PlanarVec2_Check(self));
    return Vec2_result(self, -self->y, self->x);
}

static PyMethodDef Vec2_methods[] = {
    {"polar", (PyCFunction)Vec2_new_polar, 
        METH_CLASS | METH_VARARGS | METH_KEYWORDS, 
        "Create a vector from polar coordinates."},
    {"almost_equals", (PyCFunction)Vec2_almost_equals, METH_O, 
        "Compare vectors for approximate equality."},
    {"angle_to", (PyCFunction)Vec2_angle_to, METH_O, 
        "Compute the smallest angle from this vector to another."},
    {"distance_to", (PyCFunction)Vec2_distance_to, METH_O, 
        "Compute the distance to another point vector."},
    {"dot", (PyCFunction)Vec2_dot, METH_O, 
        "Compute the dot product with another vector."},
    {"cross", (PyCFunction)Vec2_cross, METH_O, 
        "Compute the cross product with another vector."},
    {"rotated", (PyCFunction)Vec2_rotated, METH_O, 
        "Compute the vector rotated by an angle, in degrees."},
    {"scaled_to", (PyCFunction)Vec2_scaled_to, METH_O, 
        "Compute the vector scaled to a given length. "
        "If the vector is null, the null vector is returned."},
    {"project", (PyCFunction)Vec2_project, METH_O, 
        "Compute the projection of another vector onto this one."},
    {"reflect", (PyCFunction)Vec2_reflect, METH_O, 
        "Compute the reflection of this vector against another."},
    {"clamped", (PyCFunction)Vec2_clamped, METH_VARARGS | METH_KEYWORDS, 
        "Compute a vector in the same direction with a bounded length."},
    {"lerp", (PyCFunction)Vec2_lerp, METH_VARARGS, 
        "Compute a vector by linear interpolation between "
        "this vector and another."},
    {"normalized", (PyCFunction)Vec2_normalized, METH_NOARGS, 
        "Return the vector scaled to unit length. "
        "If the vector is null, the null vector is returned."},
    {"perpendicular", (PyCFunction)Vec2_perpendicular, METH_NOARGS, 
        "Compute the perpendicular vector."},
    {NULL, NULL}
};

/* Arithmetic operations */

static PyObject *
Vec2__add__(PyObject *a, PyObject *b)
{
    double ax, ay, bx, by;

    if (PlanarVec2_Parse(a, &ax, &ay) && PlanarVec2_Parse(b, &bx, &by)) {
        return (PyObject *)PlanarVec2_FromDoubles(ax + bx, ay + by);
    } else {
        PyErr_Clear();
        Py_INCREF(Py_NotImplemented);
        return Py_NotImplemented;
    }
}

static PyObject *
Vec2__sub__(PyObject *a, PyObject *b)
{
    double ax, ay, bx, by;

    if (PlanarVec2_Parse(a, &ax, &ay) && PlanarVec2_Parse(b, &bx, &by)) {
        return (PyObject *)PlanarVec2_FromDoubles(ax - bx, ay - by);
    } else {
        PyErr_Clear();
        Py_INCREF(Py_NotImplemented);
        return Py_NotImplemented;
    }
}

static PyObject *
Vec2__mul__(PyObject *a, PyObject *b)
{
    int a_is_vec, b_is_vec;
    double ax, ay, bx, by;

    a_is_vec = PlanarVec2_Parse(a, &ax, &ay);
    b_is_vec = PlanarVec2_Parse(b, &bx, &by);

    if (a_is_vec && b_is_vec) {
        return (PyObject *)PlanarVec2_FromDoubles(ax * bx, ay * by);
    } else if (a_is_vec) {
        b = PyObject_ToFloat(b);
        if (b != NULL) {
            bx = PyFloat_AS_DOUBLE(b);
            a = (PyObject *)PlanarVec2_FromDoubles(ax * bx, ay * bx);
            Py_DECREF(b);
            PyErr_Clear();
            return a;
        }
    } else if (b_is_vec) {
        a = PyObject_ToFloat(a);
        if (a != NULL) {
            ax = PyFloat_AS_DOUBLE(a);
            b = (PyObject *)PlanarVec2_FromDoubles(bx * ax, by * ax);
            Py_DECREF(a);
            PyErr_Clear();
            return b;
        }
    }
    PyErr_Clear();
    Py_INCREF(Py_NotImplemented);
    return Py_NotImplemented;
}

static PyObject *
Vec2__truediv__(PyObject *a, PyObject *b)
{
    int a_is_vec, b_is_vec;
    double ax, ay, bx, by;

    a_is_vec = PlanarVec2_Parse(a, &ax, &ay);
    b_is_vec = PlanarVec2_Parse(b, &bx, &by);

    if (a_is_vec && b_is_vec) {
        if (!bx || !by) {
            goto div_by_zero;
        }
        return (PyObject *)PlanarVec2_FromDoubles(ax / bx, ay / by);
    } else if (a_is_vec) {
        b = PyObject_ToFloat(b);
        if (b != NULL) {
            bx = PyFloat_AS_DOUBLE(b);
            if (!bx) {
                goto div_by_zero;
            }
            a = (PyObject *)PlanarVec2_FromDoubles(ax / bx, ay / bx);
            Py_DECREF(b);
            PyErr_Clear();
            return a;
        }
    } else if (b_is_vec) {
        a = PyObject_ToFloat(a);
        if (a != NULL) {
            ax = PyFloat_AS_DOUBLE(a);
            if (!bx || !by) {
                goto div_by_zero;
            }
            b = (PyObject *)PlanarVec2_FromDoubles(ax / bx, ax / by);
            Py_DECREF(a);
            PyErr_Clear();
            return b;
        }
    }
    PyErr_Clear();
    Py_INCREF(Py_NotImplemented);
    return Py_NotImplemented;

div_by_zero:
    PyErr_SetString(PyExc_ZeroDivisionError, "Vec2 division by zero");
    return NULL;
}

static PyObject *
Vec2__floordiv__(PyObject *a, PyObject *b)
{
    PyObject *q;
    PlanarVec2Object *v;
    q = Vec2__truediv__(a, b);
    if (q != NULL && q != Py_NotImplemented) {
        /* Since q is a new vector, not referenced from outside,
           we can modify it here without breaking immutability */
        v = (PlanarVec2Object *)q;
        v->x = floor(v->x);
        v->y = floor(v->y);
    }
    return q;
}

static PlanarVec2Object *
Vec2__pos__(PlanarVec2Object *self)
{
    Py_INCREF(self);
    return self;
}

static PlanarVec2Object *
Vec2__neg__(PlanarVec2Object *self)
{
    assert(PlanarVec2_Check(self));
    return Vec2_result(self, -self->x, -self->y);
}

static int
Vec2__nonzero__(PlanarVec2Object *self)
{
    assert(PlanarVec2_Check(self));
    return self->x != 0.0 || self->y != 0.0;
}

static PyNumberMethods Vec2_as_number = {
    (binaryfunc)Vec2__add__,       /* binaryfunc nb_add */
    (binaryfunc)Vec2__sub__,       /* binaryfunc nb_subtract */
    (binaryfunc)Vec2__mul__,       /* binaryfunc nb_multiply */
#if PY_MAJOR_VERSION < 3
    0,       /* binaryfunc nb_div */
#endif
    0,       /* binaryfunc nb_remainder */
    0,       /* binaryfunc nb_divmod */
    0,       /* ternaryfunc nb_power */
    (unaryfunc)Vec2__neg__,       /* unaryfunc nb_negative */
    (unaryfunc)Vec2__pos__,       /* unaryfunc nb_positive */
    (unaryfunc)Vec2_get_length,   /* unaryfunc nb_absolute */
    (inquiry)Vec2__nonzero__,       /* inquiry nb_bool */
    0,       /* unaryfunc nb_invert */
    0,       /* binaryfunc nb_lshift */
    0,       /* binaryfunc nb_rshift */
    0,       /* binaryfunc nb_and */
    0,       /* binaryfunc nb_xor */
    0,       /* binaryfunc nb_or */
#if PY_MAJOR_VERSION < 3
    0,       /* coercion nb_coerce */
#endif
    0,       /* unaryfunc nb_int */
    0,       /* void *nb_reserved */
    0,       /* unaryfunc nb_float */
#if PY_MAJOR_VERSION < 3
    0,       /* binaryfunc nb_oct */
    0,       /* binaryfunc nb_hex */
#endif

    (binaryfunc)Vec2__add__,       /* binaryfunc nb_inplace_add */
    (binaryfunc)Vec2__sub__,       /* binaryfunc nb_inplace_subtract */
    (binaryfunc)Vec2__mul__,       /* binaryfunc nb_inplace_multiply */
#if PY_MAJOR_VERSION < 3
    0,       /* binaryfunc nb_inplace_divide */
#endif
    0,       /* binaryfunc nb_inplace_remainder */
    0,       /* ternaryfunc nb_inplace_power */
    0,       /* binaryfunc nb_inplace_lshift */
    0,       /* binaryfunc nb_inplace_rshift */
    0,       /* binaryfunc nb_inplace_and */
    0,       /* binaryfunc nb_inplace_xor */
    0,       /* binaryfunc nb_inplace_or */

    (binaryfunc)Vec2__floordiv__,    /* binaryfunc nb_floor_divide */
    (binaryfunc)Vec2__truediv__,     /* binaryfunc nb_true_divide */
    (binaryfunc)Vec2__floordiv__,    /* binaryfunc nb_inplace_floor_divide */
    (binaryfunc)Vec2__truediv__,     /* binaryfunc nb_inplace_true_divide */

    0,       /* unaryfunc nb_index */
};

/* Sequence protocol methods */

static Py_ssize_t
Vec2_len(PyObject *self)
{
    return 2;
}

static PyObject *
Vec2_getitem(PlanarVec2Object *self, Py_ssize_t i)
{
    switch (i) {
        case 0:
            return PyFloat_FromDouble(self->x);
        case 1:
            return PyFloat_FromDouble(self->y);
        default:
            return NULL;
    }
}

static PySequenceMethods Vec2_as_sequence = {
    (lenfunc)Vec2_len,      /* sq_length */
    0,                      /*sq_concat*/
    0,                      /*sq_repeat*/
    (ssizeargfunc)Vec2_getitem, /*sq_item*/
    0,                      /* sq_slice */
    0,                      /* sq_ass_item */
};

PyDoc_STRVAR(Vec2_doc, 
    "Two dimensional immutable vector.\n\n"
    "Vec2(x, y)"
);

PyTypeObject PlanarVec2Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "planar.Vec2",       /* tp_name */
    sizeof(PlanarVec2Object), /* tp_basicsize */
    0,                    /* tp_itemsize */
    (destructor)Vec2_dealloc, /* tp_dealloc */
    0,                    /* tp_print */
    0,                    /* tp_getattr */
    0,                    /* tp_setattr */
    0,                    /* reserved */
    (reprfunc)Vec2_repr,  /* tp_repr */
    &Vec2_as_number,      /* tp_as_number */
    &Vec2_as_sequence,    /* tp_as_sequence */
    0,                    /* tp_as_mapping */
    (hashfunc)Vec2_hash,  /* tp_hash */
    0,                    /* tp_call */
    (reprfunc)Vec2_str,   /* tp_str */
    0, /* PyObject_GenericGetAttr, */                   /* tp_getattro */
    0,/* PyObject_GenericSetAttr, */                    /* tp_setattro */
    0,                    /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_CHECKTYPES,   /* tp_flags */
    Vec2_doc,          /* tp_doc */
    0,                    /* tp_traverse */
    0,                    /* tp_clear */
    Vec2_compare,         /* tp_richcompare */
    0,                    /* tp_weaklistoffset */
    0,                    /* tp_iter */
    0,                    /* tp_iternext */
    Vec2_methods,                    /* tp_methods */
    0,                    /* tp_members */
    Vec2_getset,                    /* tp_getset */
    0,                    /* tp_base */
    0,                    /* tp_dict */
    0,                    /* tp_descr_get */
    0,                    /* tp_descr_set */
    0,                    /* tp_dictoffset */
    (initproc)Vec2_init,  /* tp_init */
    Vec2_alloc,           /* tp_alloc */
    0,          /* tp_new */
    0,              /* tp_free */
};

/***************************************************************************/

static PlanarSeq2Object *
Seq2_alloc(PyTypeObject *type, Py_ssize_t size)
{
    PlanarSeq2Object *varray = 
	(PlanarSeq2Object *)type->tp_alloc(type, size);
    if (varray == NULL) {
		return NULL;
    }
    if (varray->vec == NULL) {
		/* Space allocated inline */
		varray->vec = varray->data;
    }
    return varray;
}

static PlanarSeq2Object *
Seq2_new_from_points(PyTypeObject *type, PyObject *points)
{
    PlanarSeq2Object *varray;
    Py_ssize_t size;
    Py_ssize_t i;

    if (PlanarSeq2_Check(points)) {
		/* Copy existing Seq2 (optimized) */
		varray = Seq2_alloc(type, Py_SIZE(points));
		if (varray == NULL) {
			return NULL;
		}
		memcpy(varray->vec, ((PlanarSeq2Object *)points)->vec, 
			sizeof(planar_vec2_t) * size);
    } else {
		/* Generic iterable of points */
		points = PySequence_Fast(points, 
			"expected iterable of Vec2 objects");
		if (points == NULL) {
			return NULL;
		}
		size = PySequence_Fast_GET_SIZE(points);
		varray = Seq2_alloc(type, size);
		if (varray == NULL) {
			Py_DECREF(points);
			return NULL;
		}
		for (i = 0; i < size; ++i) {
			if (!PlanarVec2_Parse(PySequence_Fast_GET_ITEM(points, i), 
			&varray->vec[i].x, &varray->vec[i].y)) {
			PyErr_SetString(PyExc_TypeError,
				"expected iterable of Vec2 objects");
			Py_DECREF(varray);
			Py_DECREF(points);
			return NULL;
			}
		}
		Py_DECREF(points);
    }
    return varray;
}

static PlanarSeq2Object *
Seq2_new(PyTypeObject *type, PyObject *args, PyObject *kwargs)
{
    PlanarSeq2Object *varray;
    PyObject *vectors;
    Py_ssize_t size;
    int i;

    if (kwargs != NULL) {
        PyErr_SetString(PyExc_TypeError, "invalid keyword argument");
		return NULL;
    }
    if (PyTuple_GET_SIZE(args) != 1) {
        PyErr_SetString(PyExc_TypeError, "wrong number of arguments");
        return NULL;
    }
    return Seq2_new_from_points(type, PyTuple_GET_ITEM(args, 0));
}

static void
Seq2_dealloc(PyObject *self)
{
    Py_TYPE(self)->tp_free(self);
}

static PyObject *
Seq2_compare(PyObject *a, PyObject *b, int op)
{
    Py_ssize_t size, osize;
    planar_vec2_t *av, *bv;

    size = PySequence_Size(a);
    osize = PySequence_Size(b);
    if (size == osize && size != -1 
	&& PlanarSeq2_Check(a) && Py_TYPE(a) == Py_TYPE(b)) {
	av = ((PlanarSeq2Object *)a)->vec;
	bv = ((PlanarSeq2Object *)b)->vec;
	switch (op) {
            case Py_EQ:
		while (size--) {
		    if (av->x != bv->x || av->y != bv->y) {
			Py_RETURN_FALSE;
		    }
		    ++av;
		    ++bv;
		}
                Py_RETURN_TRUE;
            case Py_NE:
		while (size--) {
		    if (av->x != bv->x || av->y != bv->y) {
			Py_RETURN_TRUE;
		    }
		    ++av;
		    ++bv;
		}
                Py_RETURN_FALSE;
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

/* Sequence Methods */

static PyObject *
Seq2_getitem(PlanarSeq2Object *self, Py_ssize_t index)
{
    Py_ssize_t size = PySequence_Size((PyObject *)self);
    if (size == -1) {
	return NULL;
    }
    if (index >= 0 && index < size) {
        return (PyObject *)PlanarVec2_FromStruct(self->vec + index);
    }
    PyErr_Format(PyExc_IndexError, "index %d out of range", (int)index);
    return NULL;
}

static int
Seq2_assitem(PlanarSeq2Object *self, Py_ssize_t index, PyObject *v)
{
    double x, y;
    Py_ssize_t size = PySequence_Size((PyObject *)self);
    if (size == -1) {
	return -1;
    }
    if (index >= 0 && index < size) {
	if (!PlanarVec2_Parse(v, &x, &y)) {
	    if (!PyErr_Occurred()) {
		PyErr_Format(PyExc_TypeError, 
		    "Cannot assign %.200s into %.200s",
		    v->ob_type->tp_name, self->ob_type->tp_name);
	    }
	    return -1;
	}
        self->vec[index].x = x;
        self->vec[index].y = y;
        return 0;
    }
    PyErr_Format(PyExc_IndexError, 
	"assignment index %d out of range", (int)index);
    return -1;
}

static Py_ssize_t
Seq2_length(PlanarSeq2Object *self)
{
    return Py_SIZE(self);
}

static PySequenceMethods Seq2_as_sequence = {
	(lenfunc)Seq2_length,	/* sq_length */
	0,		/*sq_concat*/
	0,		/*sq_repeat*/
	(ssizeargfunc)Seq2_getitem,		/*sq_item*/
	0,		/* sq_slice */
	(ssizeobjargproc)Seq2_assitem,	/* sq_ass_item */
};

/* Methods */

static PyObject *
Seq2_almost_equals(PlanarSeq2Object *self, PlanarSeq2Object *other)
{
    double dx, dy;
    Py_ssize_t size, osize;
    planar_vec2_t *sv, *ov;

    assert(PlanarSeq2_Check(self));
    size = PySequence_Size((PyObject *)self);
    osize = PySequence_Size((PyObject *)other);
    if (Py_TYPE(self) != Py_TYPE(other) || size == -1 || osize == -1) {
	CONVERSION_ERROR();
    }
    if (size == osize) {
	sv = self->vec;
	ov = other->vec;
	while (size--) {
	    dx = sv->x - ov->x;
	    dy = sv->y - ov->y;
	    if (dx*dx + dy*dy > PLANAR_EPSILON2) {
		Py_RETURN_FALSE;
	    }
	    ++sv;
	    ++ov;
	}
	Py_RETURN_TRUE;
    }
    Py_RETURN_FALSE;
}

static PlanarSeq2Object *
Seq2_copy(PlanarSeq2Object *self)
{
    PlanarSeq2Object *varray;
    Py_ssize_t size;
    
    assert(PlanarSeq2_Check(self));
    size = PySequence_Size((PyObject *)self);
    if (size == -1) {
	return NULL;
    }
    varray = Seq2_alloc(Py_TYPE(self), size);
    if (varray == NULL) {
	return NULL;
    }
    memcpy(varray->vec, self->vec, sizeof(planar_vec2_t) * size);
    return varray;
}

static PyMethodDef Seq2_methods[] = {
    {"almost_equals", (PyCFunction)Seq2_almost_equals, METH_O, 
	"Compare for approximate equality."},
    {"from_points", (PyCFunction)Seq2_new_from_points, METH_CLASS, 
	"Create a new 2D sequence from an iterable of points"},
    {"__copy__", (PyCFunction)Seq2_copy, METH_NOARGS, NULL}, 
    {NULL, NULL}
};

/* Arithmetic Operations */

static PyObject *
Seq2__mul__(PyObject *a, PyObject *b)
{
    PlanarSeq2Object *src, *dst;
    PlanarAffineObject *t;
    planar_vec2_t *srcv, *dstv;
    Py_ssize_t size;
    double ta, tb, tc, td, te, tf;

    if (PlanarSeq2_Check(a) && PlanarAffine_Check(b)) {
	src = (PlanarSeq2Object *)a;
	t = (PlanarAffineObject *)b;
    } else if (PlanarSeq2_Check(b) && PlanarAffine_Check(a)) {
	src = (PlanarSeq2Object *)b;
	t = (PlanarAffineObject *)a;
    } else {
	/* We support only transform operations */
	RETURN_NOT_IMPLEMENTED;
    }
    ta = t->a;
    tb = t->b;
    tc = t->c;
    td = t->d;
    te = t->e;
    tf = t->f;

    size = PySequence_Size((PyObject *)src);
    if (size == -1) {
	return NULL;
    }
    dst = Seq2_alloc(Py_TYPE(src), size);
    if (dst == NULL) {
	return NULL;
    }
    srcv = src->vec;
    dstv = dst->vec;
    while (size--) {
	dstv->x = srcv->x*ta + srcv->y*td + tc;
	dstv->y = srcv->x*tb + srcv->y*te + tf;
	++srcv;
	++dstv;
    }
    return (PyObject *)dst;
}

static PyObject *
Seq2__imul__(PyObject *a, PyObject *b)
{
    PlanarSeq2Object *s;
    PlanarAffineObject *t;
    planar_vec2_t *sv;
    Py_ssize_t size;
    double ta, tb, tc, td, te, tf;

    if (PlanarSeq2_Check(a) && PlanarAffine_Check(b)) {
	s = (PlanarSeq2Object *)a;
	t = (PlanarAffineObject *)b;
    } else if (PlanarSeq2_Check(b) && PlanarAffine_Check(a)) {
	s = (PlanarSeq2Object *)b;
	t = (PlanarAffineObject *)a;
    } else {
	/* We support only transform operations */
	RETURN_NOT_IMPLEMENTED;
    }
    ta = t->a;
    tb = t->b;
    tc = t->c;
    td = t->d;
    te = t->e;
    tf = t->f;

    size = PySequence_Size((PyObject *)s);
    if (size == -1) {
	return NULL;
    }
    sv = s->vec;
    while (size--) {
	sv->x = sv->x*ta + sv->y*td + tc;
	sv->y = sv->x*tb + sv->y*te + tf;
	++sv;
    }
    Py_INCREF(s);
    return (PyObject *)s;
}

static PyNumberMethods Seq2_as_number = {
    0,       /* binaryfunc nb_add */
    0,       /* binaryfunc nb_subtract */
    (binaryfunc)Seq2__mul__,       /* binaryfunc nb_multiply */
#if PY_MAJOR_VERSION < 3
    0,       /* binaryfunc nb_div */
#endif
    0,       /* binaryfunc nb_remainder */
    0,       /* binaryfunc nb_divmod */
    0,       /* ternaryfunc nb_power */
    0,       /* unaryfunc nb_negative */
    0,       /* unaryfunc nb_positive */
    0,       /* unaryfunc nb_absolute */
    0,       /* inquiry nb_bool */
    0,       /* unaryfunc nb_invert */
    0,       /* binaryfunc nb_lshift */
    0,       /* binaryfunc nb_rshift */
    0,       /* binaryfunc nb_and */
    0,       /* binaryfunc nb_xor */
    0,       /* binaryfunc nb_or */
#if PY_MAJOR_VERSION < 3
    0,       /* coercion nb_coerce */
#endif
    0,       /* unaryfunc nb_int */
    0,       /* void *nb_reserved */
    0,       /* unaryfunc nb_float */
#if PY_MAJOR_VERSION < 3
    0,       /* binaryfunc nb_oct */
    0,       /* binaryfunc nb_hex */
#endif

    0,       /* binaryfunc nb_inplace_add */
    0,       /* binaryfunc nb_inplace_subtract */
    (binaryfunc)Seq2__imul__,       /* binaryfunc nb_inplace_multiply */
#if PY_MAJOR_VERSION < 3
    0,       /* binaryfunc nb_inplace_divide */
#endif
    0,       /* binaryfunc nb_inplace_remainder */
    0,       /* ternaryfunc nb_inplace_power */
    0,       /* binaryfunc nb_inplace_lshift */
    0,       /* binaryfunc nb_inplace_rshift */
    0,       /* binaryfunc nb_inplace_and */
    0,       /* binaryfunc nb_inplace_xor */
    0,       /* binaryfunc nb_inplace_or */

    0,       /* binaryfunc nb_floor_divide */
    0,       /* binaryfunc nb_true_divide */
    0,       /* binaryfunc nb_inplace_floor_divide */
    0,       /* binaryfunc nb_inplace_true_divide */

    0,       /* unaryfunc nb_index */
};


PyDoc_STRVAR(Seq2__doc__, "Fixed length vector sequence");

PyTypeObject PlanarSeq2Type = {
	PyObject_HEAD_INIT(NULL)
	0,			        /*ob_size*/
	"planar.Seq2",		/*tp_name*/
	sizeof(PlanarSeq2Object),	/*tp_basicsize*/
	sizeof(planar_vec2_t),		/*tp_itemsize*/
	/* methods */
	(destructor)Seq2_dealloc, /*tp_dealloc*/
	0,			       /*tp_print*/
	0,                      /*tp_getattr*/
	0,                      /*tp_setattr*/
	0,		        /*tp_compare*/
	0,                      /*tp_repr*/
	&Seq2_as_number,        /*tp_as_number*/
	&Seq2_as_sequence,      /*tp_as_sequence*/
	0,	                /*tp_as_mapping*/
	0,	                /*tp_hash*/
	0,                      /*tp_call*/
	0,                      /*tp_str*/
	0,                      /*tp_getattro*/
	0,                      /*tp_setattro*/
	0,                      /*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_CHECKTYPES,     /*tp_flags*/
	Seq2__doc__,            /*tp_doc*/
	0,                      /*tp_traverse*/
	0,                      /*tp_clear*/
	Seq2_compare,           /*tp_richcompare*/
	0,                      /*tp_weaklistoffset*/
	0,                      /*tp_iter*/
	0,                      /*tp_iternext*/
	Seq2_methods,           /*tp_methods*/
	0,                      /*tp_members*/
	0,                      /*tp_getset*/
	0,                      /*tp_base*/
	0,                      /*tp_dict*/
	0,                      /*tp_descr_get*/
	0,                      /*tp_descr_set*/
	0,                      /*tp_dictoffset*/
	0,                      /*tp_init*/
	0,                      /*tp_alloc*/
	(newfunc)Seq2_new,      /*tp_new*/
	0,                      /*tp_free*/
	0,                      /*tp_is_gc*/
};

/***************************************************************************/

static PlanarVec2ArrayObject *
Vec2Array_alloc(PyTypeObject *type, Py_ssize_t size)
{
    PlanarVec2ArrayObject *varray = 
		(PlanarVec2ArrayObject *)_PyObject_NewVar(type, size);
    if (varray == NULL) {
		return NULL;
    }
    varray->vec = PyMem_Malloc(size * sizeof(planar_vec2_t));
    if (varray->vec == NULL) {
		Py_DECREF(varray);
		return (PlanarVec2ArrayObject *)PyErr_NoMemory();
    }
	varray->allocated = size;
    return varray;
}

static void
Vec2Array_dealloc(PlanarVec2ArrayObject *self)
{
    if (self->vec != NULL) {
		PyMem_Free(self->vec);
		self->vec = NULL;
    }
    Py_TYPE(self)->tp_free(self);
}

static PlanarVec2ArrayObject *
Vec2Array_new(PyTypeObject *type, PyObject *args, PyObject *kwargs)
{
    PlanarVec2ArrayObject *varray;
    PyObject *vectors;
    Py_ssize_t size;
    int i;

    if (kwargs != NULL) {
        PyErr_SetString(PyExc_TypeError, "invalid keyword argument");
		return NULL;
    }
    if (PyTuple_GET_SIZE(args) == 0) {
		return (PlanarVec2ArrayObject *)type->tp_alloc(type, 0);
    } else if (PyTuple_GET_SIZE(args) == 1) {
		return (PlanarVec2ArrayObject *)Seq2_new_from_points(
			type, PyTuple_GET_ITEM(args, 0));
	} else {
        PyErr_SetString(PyExc_TypeError, "wrong number of arguments");
        return NULL;
	}
}

static int
Vec2Array_resize(PlanarVec2ArrayObject *self, Py_ssize_t newsize) 
{
	Py_ssize_t new_allocated;
	Py_ssize_t allocated = self->allocated;
	void *realloc_vec;

	/* Bypass realloc() when a previous overallocation is large enough
	   to accommodate the newsize.  If the newsize falls lower than half
	   the allocated size, then proceed with the realloc() to shrink the array.
	*/
	if (allocated >= newsize && newsize >= (allocated >> 1)) {
		Py_SIZE(self) = newsize;
		return 0;
	}

	/* Growth pattern derived from CPython list implementation
	 * The growth pattern is:  0, 4, 8, 16, 25, 35, 46, 58, 72, 88, ...
	 */
	new_allocated = (newsize >> 3) + (newsize < 9 ? 3 : 6);

	/* check for integer overflow */
	if (new_allocated > PY_SIZE_MAX - newsize) {
		PyErr_NoMemory();
		return -1;
	} else {
		new_allocated += newsize;
	}

	if (newsize == 0) {
		new_allocated = 0;
	}
	realloc_vec = PyMem_Realloc(
		self->vec, new_allocated * sizeof(planar_vec2_t));
	if (realloc_vec == NULL) {
		PyErr_NoMemory();
		return -1;
	}
	self->vec = (planar_vec2_t *)realloc_vec;
	self->allocated = new_allocated;
	Py_SIZE(self) = newsize;
	return 0;
}

static PyObject *
Vec2Array_append(PlanarVec2ArrayObject *self, PyObject *vector) 
{
	double x, y;
	Py_ssize_t i = Py_SIZE(self);

	if (i == PY_SSIZE_T_MAX) {
		PyErr_SetString(PyExc_OverflowError,
			"cannot add more objects to array");
		return NULL;
	}
	if (!PlanarVec2_Parse(vector, &x, &y)) {
		if (!PyErr_Occurred()) {
			PyErr_Format(PyExc_TypeError, 
				"Cannot append %.200s to %.200s",
				vector->ob_type->tp_name, self->ob_type->tp_name);
	    }
		return NULL;
	}
	if (Vec2Array_resize(self, i + 1) == -1) {
		return NULL;
	}
	self->vec[i].x = x;
	self->vec[i].y = y;

	Py_RETURN_NONE;
}

static PyObject *
Vec2Array_insert(PlanarVec2ArrayObject *self, PyObject *args)
{
	double x, y;
	PyObject *vector; 
	Py_ssize_t where;
	Py_ssize_t n = Py_SIZE(self);

    assert(PlanarVec2Array_Check(self));
	if (!PyArg_ParseTuple(args, "nO:insert", &where, &vector)) {
		return NULL;
	}
	if (n == PY_SSIZE_T_MAX) {
		PyErr_SetString(PyExc_OverflowError,
			"cannot add more objects to array");
		return NULL;
	}
	if (!PlanarVec2_Parse(vector, &x, &y)) {
		if (!PyErr_Occurred()) {
			PyErr_Format(PyExc_TypeError, 
				"Cannot insert %.200s into %.200s",
				vector->ob_type->tp_name, self->ob_type->tp_name);
	    }
		return NULL;
	}
	if (Vec2Array_resize(self, n + 1) == -1) {
		return NULL;
	}
	if (where < 0) {
		where += n;
		if (where < 0) {
			where = 0;
		}
	}
	if (where > n) {
		where = n;
	}
	memmove(&self->vec[where + 1], &self->vec[where], 
		(n - where) * sizeof(planar_vec2_t));
	self->vec[where].x = x;
	self->vec[where].y = y;

	Py_RETURN_NONE;
}

static PyObject *
Vec2Array_extend(
	PlanarVec2ArrayObject *self, PyObject *vectors) 
{
	double x, y;
	Py_ssize_t size, j;
	Py_ssize_t i = Py_SIZE(self);

    if (PlanarSeq2_Check(vectors)) {
		/* Concat existing Seq2 (optimized) */
		size = Py_SIZE(vectors);
		if (Vec2Array_resize(self, i + size) == -1) {
			return NULL;
		}
		memcpy(&self->vec[i], ((PlanarSeq2Object *)vectors)->vec, 
			sizeof(planar_vec2_t) * size);
    } else {
		/* Generic iterable of points */
		vectors = PySequence_Fast(vectors, 
			"expected iterable of Vec2 objects");
		if (vectors == NULL) {
			return NULL;
		}
		size = PySequence_Fast_GET_SIZE(vectors);
		if (Vec2Array_resize(self, i + size) == -1) {
			Py_DECREF(vectors);
			return NULL;
		}
		for (j = 0; j < size; ++j, ++i) {
			if (!PlanarVec2_Parse(PySequence_Fast_GET_ITEM(vectors, j), 
				&self->vec[i].x, &self->vec[i].y)) {
				PyErr_SetString(PyExc_TypeError,
					"expected iterable of Vec2 objects");
				Py_DECREF(vectors);
				return NULL;
			}
		}
		Py_DECREF(vectors);
    }
	Py_RETURN_NONE;
}

static PlanarVec2ArrayObject *
Vec2Array_slice(PlanarVec2ArrayObject *self, 
	Py_ssize_t ilow, Py_ssize_t ihigh)
{
	PlanarVec2ArrayObject *result;
	Py_ssize_t len;

	if (ilow < 0) {
		ilow = 0;
	} else if (ilow > Py_SIZE(self)) {
		ilow = Py_SIZE(self);
	}
	if (ihigh < ilow) {
		ihigh = ilow;
	} else if (ihigh > Py_SIZE(self)) {
		ihigh = Py_SIZE(self);
	}
	len = ihigh - ilow;

	result = (PlanarVec2ArrayObject *)Py_TYPE(self)->tp_alloc(
		Py_TYPE(self), len);
	if (result == NULL) {
		return NULL;
	}
	memcpy(result->vec, &self->vec[ilow], sizeof(planar_vec2_t) * len);
	return result;
}

static int
Vec2Array_ass_slice(PlanarVec2ArrayObject *self, 
	Py_ssize_t ilow, Py_ssize_t ihigh, PyObject *vectors)
{
	Py_ssize_t n; /* # of elements in replacement array */
	Py_ssize_t norig; /* # of elements in list getting replaced */
	Py_ssize_t d; /* Change in size */
	Py_ssize_t j;

	if (vectors == NULL) {
		n = 0;
	} else if (PlanarSeq2_Check(vectors)) {
		Py_INCREF(vectors);
		n = Py_SIZE(vectors);
	} else {
		vectors = PySequence_Fast(vectors, 
			"can only assign an iterable of vectors");
		if (vectors == NULL) {
			goto error;
		}
		n = PySequence_Fast_GET_SIZE(vectors);
	}
	if (ilow < 0) {
		ilow = 0;
	} else if (ilow > Py_SIZE(self)) {
		ilow = Py_SIZE(self);
	}
	if (ihigh < ilow) {
		ihigh = ilow;
	} else if (ihigh > Py_SIZE(self)) {
		ihigh = Py_SIZE(self);
	}

	norig = ihigh - ilow;
	assert(norig >= 0);
	d = n - norig;
	if (Py_SIZE(self) + d == 0) {
		Py_DECREF(vectors);
		return Vec2Array_resize(self, 0);
	}
	if (d < 0) { /* Delete -d items */
		memmove(&self->vec[ihigh + d], &self->vec[ihigh],
			sizeof(planar_vec2_t) * (Py_SIZE(self) - ihigh));
	}
	if (Vec2Array_resize(self, Py_SIZE(self) + d) < 0) {
		goto error;
	}
	if (d > 0) { /* Insert d items */
		memmove(&self->vec[ihigh + d], &self->vec[ihigh],
			sizeof(planar_vec2_t) * (Py_SIZE(self) - ihigh));
	}
	if (PlanarSeq2_Check(vectors)) {
		memmove(&self->vec[ilow], &((PlanarSeq2Object *)vectors)->vec, 
		n * sizeof(planar_vec2_t));
	} else {
		for (j = 0; j < n; ++j, ++ilow) {
			if (!PlanarVec2_Parse(PySequence_Fast_GET_ITEM(vectors, j), 
				&self->vec[ilow].x, &self->vec[ilow].y)) {
				PyErr_SetString(PyExc_TypeError,
					"expected iterable of Vec2 objects");
				goto error;
			}
		}
	}
	Py_DECREF(vectors);
	return 0;
 error:
	Py_XDECREF(vectors);
	return -1;
}

static int
Vec2Array_ass_item(PlanarVec2ArrayObject *self, Py_ssize_t i, PyObject *vector)
{
	double x, y;

	if (i < 0 || i >= Py_SIZE(self)) {
		PyErr_SetString(PyExc_IndexError,
				"assignment index out of range");
		return -1;
	}
	if (vector == NULL) {
		return Vec2Array_ass_slice(self, i, i+1, vector);
	}
	if (!PlanarVec2_Parse(vector, &x, &y)) {
		if (!PyErr_Occurred()) {
			PyErr_Format(PyExc_TypeError, 
				"Cannot assign item %.200s into %.200s",
				vector->ob_type->tp_name, self->ob_type->tp_name);
	    }
		return -1;
	}
	self->vec[i].x = x;
	self->vec[i].y = y;
	return 0;
}

static PySequenceMethods Vec2Array_as_sequence = {
	(lenfunc)Seq2_length,	/* sq_length */
	0,		/*sq_concat*/
	0,		/*sq_repeat*/
	(ssizeargfunc)Seq2_getitem,                 /* sq_item */
	(ssizessizeargfunc)Vec2Array_slice,         /* sq_slice */
	(ssizeobjargproc)Vec2Array_ass_item,        /* sq_ass_item */
	(ssizessizeobjargproc)Vec2Array_ass_slice,  /* sq_ass_slice */
	0,		/* sq_contains */
};

static PyMethodDef Vec2Array_methods[] = {
    {"append", (PyCFunction)Vec2Array_append, METH_O, 
		"Append all vectors in iterable to the end of the array."},
    {"insert", (PyCFunction)Vec2Array_insert, METH_VARARGS, 
		"Insert a vector at the specified index."},
    {"extend", (PyCFunction)Vec2Array_extend, METH_O, 
		"Extend an array appending vectors from the given sequence."},
    {NULL, NULL}
};

PyDoc_STRVAR(Vec2Array__doc__, "Dynamic vector array");

PyTypeObject PlanarVec2ArrayType = {
	PyObject_HEAD_INIT(NULL)
	0,			        /*ob_size*/
	"planar.Vec2Array",		/*tp_name*/
	sizeof(PlanarVec2ArrayObject),	/*tp_basicsize*/
	0,		/*tp_itemsize*/
	/* methods */
	(destructor)Vec2Array_dealloc, /*tp_dealloc*/
	0,			       /*tp_print*/
	0,                      /*tp_getattr*/
	0,                      /*tp_setattr*/
	0,		        /*tp_compare*/
	0,                      /*tp_repr*/
	&Seq2_as_number,        /*tp_as_number*/
	&Vec2Array_as_sequence,      /*tp_as_sequence*/
	0,	                /*tp_as_mapping*/
	0,	                /*tp_hash*/
	0,                      /*tp_call*/
	0,                      /*tp_str*/
	0,                      /*tp_getattro*/
	0,                      /*tp_setattro*/
	0,                      /*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_CHECKTYPES,     /*tp_flags*/
	Vec2Array__doc__,       /*tp_doc*/
	0,                      /*tp_traverse*/
	0,                      /*tp_clear*/
	Seq2_compare,           /*tp_richcompare*/
	0,                      /*tp_weaklistoffset*/
	0,                      /*tp_iter*/
	0,                      /*tp_iternext*/
	Vec2Array_methods,           /*tp_methods*/
	0,                      /*tp_members*/
	0,                      /*tp_getset*/
	&PlanarSeq2Type,        /*tp_base*/
	0,                      /*tp_dict*/
	0,                      /*tp_descr_get*/
	0,                      /*tp_descr_set*/
	0,                      /*tp_dictoffset*/
	0,                      /*tp_init*/
	(allocfunc)Vec2Array_alloc,    /*tp_alloc*/
	(newfunc)Vec2Array_new,      /*tp_new*/
	0,                      /*tp_free*/
	0,                      /*tp_is_gc*/
};

