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

#ifndef PY_PLANAR_H
#define PY_PLANAR_H

/* Python 2/3 compatibility */
#if PY_MAJOR_VERSION < 3
#define PyUnicode_InternFromString(o) PyString_InternFromString(o)
#endif

#ifndef Py_TPFLAGS_CHECKTYPES /* not in Py 3 */
#define Py_TPFLAGS_CHECKTYPES 0
#endif

#if PY_MAJOR_VERSION >= 3
#define RETURN_NOT_IMPLEMENTED {  \
    Py_INCREF(Py_NotImplemented); \
    return Py_NotImplemented;     \
}
#else
#define RETURN_NOT_IMPLEMENTED {                   \
    PyErr_Format(PyExc_TypeError,                  \
        "Unorderable types: %.200s and %.200s",    \
        Py_TYPE(a)->tp_name, Py_TYPE(b)->tp_name); \
    return NULL;                                   \
}
#endif

#define CONVERSION_ERROR() {                              \
    PyErr_Format(PyExc_TypeError,                         \
        "Can't compare %.200s to %.200s",                 \
        Py_TYPE(self)->tp_name, Py_TYPE(other)->tp_name); \
    return NULL;                                          \
}

/* Math utils */
#ifndef M_PI
#define M_PI 3.14159265358979323846264338327
#endif
#define radians(d) ((d) * M_PI / 180.0)
#define degrees(d) ((d) * 180.0 / M_PI)
#define almost_eq(a, b) (fabs((a) - (b)) < PLANAR_EPSILON)

static void cos_sin_deg(double deg, double *cosout, double *sinout) 
{
	double rad;
	deg = deg >= 360.0 ? fmod(deg, 360.0) : 
		deg < 0.0 ? deg + trunc(deg * (1.0 / -360.0) + 1) * 360.0 : deg;
	
	/* Match quadrants exactly */
	if (deg == 0.0) {
		*cosout = 1.0;
		*sinout = 0.0;
	} else if (deg == 90.0) {
		*cosout = 0.0;
		*sinout = 1.0;
	} else if (deg == 180.0) {
		*cosout = -1.0;
		*sinout = 0.0;
	} else if (deg == 270.0) {
		*cosout = 0.0;
		*sinout = -1.0;
	} else {
		rad = radians(deg);
		*cosout = cos(rad);
		*sinout = sin(rad);
	}
}

/***************************************************************************/

/* Type definitions */

typedef struct {
    double x;
    double y;
} planar_vec2_t;

typedef struct {
    PyObject_HEAD
    union {
        PyObject *next_free;
        struct {double x; double y;};
    };
} PlanarVec2Object;

typedef struct {
    PyObject_VAR_HEAD
    planar_vec2_t *vec;
    /* *vec points to the data[] array, so that it can
       be positioned differently in memory in subtypes */
	union {
		planar_vec2_t data[1]; /* Used for fixed-length types */
		Py_ssize_t allocated; /* Used for variable-length types */
	};
} PlanarSeq2Object;

typedef struct {
    PyObject_HEAD
    union {
        PyObject *next_free;
        double m[6];
        struct {double a, b, c, d, e, f;};
    };
} PlanarAffineObject;

/***************************************************************************/

/* Convert the object to a float, this is designed to
   be faster and more strict than PyNumber_Float
   (it does not allow strings), but will convert
   any type that supports float conversion.

   If the argument provided is NULL, NULL is returned
   and no exception is set. If an error occurs, NULL
   is returned with an exception set. In the former
   case it is assumed that an exception has already
   been set.

   Returns: New reference
*/
static PyObject *
PyObject_ToFloat(PyObject *o) 
{
    PyNumberMethods *m;

    if (o == NULL) {
        return NULL;
    }
    if (PyFloat_Check(o)) {
        Py_INCREF(o);
        return o;
    }
	m = o->ob_type->tp_as_number;
	if (m && m->nb_float) {
        o = m->nb_float(o);
        if (o && !PyFloat_Check(o)) {
            PyErr_Format(PyExc_TypeError,
                "__float__ returned non-float (type %.200s)",
                o->ob_type->tp_name);
			Py_DECREF(o);
			return NULL;
		}
        return o;
    }
    PyErr_Format(PyExc_TypeError,
        "Can't convert %.200s to float", o->ob_type->tp_name);
    return NULL;
}

static long
hash_double(double v)
{
	/* Derived from Python 3.1.2 _Py_HashDouble() */
	long hipart;
	int expo;

	v = frexp(v, &expo);
	v *= 2147483648.0;	/* 2**31 */
	hipart = (long)v;	/* take the top 32 bits */
	v = (v - (double)hipart) * 2147483648.0; /* get the next 32 bits */
	return hipart + (long)v + (expo << 15);
}

/***************************************************************************/

extern double PLANAR_EPSILON;
extern double PLANAR_EPSILON2;

extern PyTypeObject PlanarVec2Type;
extern PyTypeObject PlanarSeq2Type;
extern PyTypeObject PlanarVec2ArrayType;
extern PyTypeObject PlanarAffineType;

extern PyObject *PlanarTransformNotInvertibleError;

/* Vec2 utils */

#define PlanarVec2_Check(op) PyObject_TypeCheck(op, &PlanarVec2Type)
#define PlanarVec2_CheckExact(op) (Py_TYPE(op) == &PlanarVec2Type)

static PlanarVec2Object *
PlanarVec2_FromDoubles(double x, double y)
{
    PlanarVec2Object *v;

    v = (PlanarVec2Object *)PlanarVec2Type.tp_alloc(&PlanarVec2Type, 0);
    if (v == NULL) {
        return NULL;
    }
    v->x = x;
    v->y = y;
    return v;
}

static PlanarVec2Object *
PlanarVec2_FromStruct(planar_vec2_t *vs)
{
    PlanarVec2Object *v;

    v = (PlanarVec2Object *)PlanarVec2Type.tp_alloc(&PlanarVec2Type, 0);
    if (v == NULL) {
        return NULL;
    }
    v->x = vs->x;
    v->y = vs->y;
    return v;
}

static int 
PlanarVec2_Parse(PyObject *o, double *x, double *y)
{
    PyObject *x_obj = NULL;
    PyObject *y_obj = NULL;
    PyObject *item;
	static char *type_err_msg = "Expected sequence of 2 numbers";

    if (PlanarVec2_Check(o)) {
        *x = ((PlanarVec2Object *)o)->x;
        *y = ((PlanarVec2Object *)o)->y;
        return 1;
    } else if (PyTuple_Check(o)) {
        /* Use fast tuple access code */
        if (PyTuple_GET_SIZE(o) != 2) {
            PyErr_SetString(PyExc_TypeError, type_err_msg);
            return 0;
        }
        x_obj = PyObject_ToFloat(PyTuple_GET_ITEM(o, 0));
        y_obj = PyObject_ToFloat(PyTuple_GET_ITEM(o, 1));
    } else if (PySequence_Check(o)) {
        /* Fall back to general sequence access */
        PyErr_SetString(PyExc_TypeError, type_err_msg);
        if (PySequence_Size(o) != 2) {
            return 0;
        }
        if ((item = PySequence_GetItem(o, 0))) {
            x_obj = PyObject_ToFloat(item);
            Py_DECREF(item);
        }
        if ((item = PySequence_GetItem(o, 1))) {
            y_obj = PyObject_ToFloat(item);
            Py_DECREF(item);
        }
	}
    if (x_obj == NULL || y_obj == NULL) {
        goto error;
    }
    *x = PyFloat_AS_DOUBLE(x_obj);
    *y = PyFloat_AS_DOUBLE(y_obj);
    Py_DECREF(x_obj);
    Py_DECREF(y_obj);
    PyErr_Clear();
    return 1;
error:
    Py_XDECREF(x_obj);
    Py_XDECREF(y_obj);
    return 0;
}

/* Seq2 utils */

#define PlanarSeq2_Check(op) PyObject_TypeCheck(op, &PlanarSeq2Type)
#define PlanarSeq2_CheckExact(op) (Py_TYPE(op) == &PlanarSeq2Type)

/* Vec2Array utils */

#define PlanarVec2Array_Check(op) PyObject_TypeCheck(op, &PlanarVec2ArrayType)
#define PlanarVec2Array_CheckExact(op) (Py_TYPE(op) == &PlanarVec2ArrayType)

/* Affine utils */

#define PlanarAffine_Check(op) PyObject_TypeCheck(op, &PlanarAffineType)
#define PlanarAffine_CheckExact(op) (Py_TYPE(op) == &PlanarAffineType)

#endif /* #ifdef PY_PLANAR_H */
