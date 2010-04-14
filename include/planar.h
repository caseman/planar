#include "Python.h"

typedef struct {
    double x;
    double y;
} planar_vec2_t;

typedef struct {
    PyObject_HEAD
    union {
        PyObject *next;
        planar_vec2_t vec;
        double member[2];
    };
} PlanarVec2Object;

PyTypeObject PlanarVec2Type;

#define PlanarVec2_Check(op) PyObject_TypeCheck(op, &PlanarVec2Type)
#define PlanarVec2_CheckExact(op) (Py_TYPE(op) == &PlanarVec2Type)
