#include "Python.h"

#ifndef PyUnicode_FromString
#define PyUnicode_FromString(o) PyString_FromString(o)
#endif

#ifndef M_PI
#define M_PI 3.14159265358979323846264338327
#endif
#define radians(d) ((d) * M_PI / 180.0)
#define degrees(d) ((d) * 180.0 / M_PI)

extern double EPSILON;
extern double EPSILON2;

typedef struct {
    double x;
    double y;
} planar_vec2_t;

typedef struct {
    PyObject_HEAD
    union {
        PyObject *next;
        struct {double x; double y;};
    };
} PlanarVec2Object;

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

PyTypeObject PlanarVec2Type;

#define PlanarVec2_Check(op) PyObject_TypeCheck(op, &PlanarVec2Type)
#define PlanarVec2_CheckExact(op) (Py_TYPE(op) == &PlanarVec2Type)

PlanarVec2Object *PlanarVec2_FromPair(double x, double y);

int Planar_ParseVec2(PyObject *o, double *x, double *y);

