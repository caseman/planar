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

/* Python 2/3 compatibility */
#ifndef PyUnicode_FromString
#define PyUnicode_FromString(o) PyString_FromString(o)
#endif
#ifndef Py_TPFLAGS_CHECKTYPES /* not in Py 3 */
#define Py_TPFLAGS_CHECKTYPES 0
#endif

#ifndef M_PI
#define M_PI 3.14159265358979323846264338327
#endif
#define radians(d) ((d) * M_PI / 180.0)
#define degrees(d) ((d) * 180.0 / M_PI)

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
PyObject *
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

/***************************************************************************/

/* We define epsilon, and a python function to modify it
   in every module. Although this is not ideal, the main alternatives is to
   use capsules, which have more overhead and aren't present in python 2.6.
   The planar.set_epsilon() function must call C _set_epsilon() function for
   each C module. This is simple and effective, if inelegant.
*/

static double EPSILON = 1e-5;
static double EPSILON2 = 1e-5 * 1e-5;

static PyObject *
_set_epsilon_func(PyObject *self, PyObject *epsilon)
{
    epsilon = PyObject_ToFloat(epsilon);
    if (epsilon == NULL) {
        return NULL;
    }

    EPSILON = PyFloat_AS_DOUBLE(epsilon);
    EPSILON2 = EPSILON * EPSILON;
    Py_DECREF(epsilon);
    Py_INCREF(Py_None);
    return Py_None;
}

#define _SET_EPSILON_FUNCDEF \
    {"_set_epsilon", (PyCFunction) _set_epsilon_func, METH_O, \
     "PRIVATE: Set epsilon value used by C extension"}

/***************************************************************************/

PyTypeObject PlanarVec2Type;

#define PlanarVec2_Check(op) PyObject_TypeCheck(op, &PlanarVec2Type)
#define PlanarVec2_CheckExact(op) (Py_TYPE(op) == &PlanarVec2Type)

PlanarVec2Object *PlanarVec2_FromPair(double x, double y);

int Planar_ParseVec2(PyObject *o, double *x, double *y);

