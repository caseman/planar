#include "Python.h"

#ifndef PyUnicode_FromString
#define PyUnicode_FromString(o) PyString_FromString(o)
#endif

#ifndef M_PI
#define M_PI 3.14159265358979323846264338327
#endif
#define radians(d) ((d) * M_PI / 180.0)
#define degrees(d) ((d) * 180.0 / M_PI)

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

PyTypeObject PlanarVec2Type;

#define PlanarVec2_Check(op) PyObject_TypeCheck(op, &PlanarVec2Type)
#define PlanarVec2_CheckExact(op) (Py_TYPE(op) == &PlanarVec2Type)

PlanarVec2Object *PlanarVec2_FromPair(double x, double y);

int Planar_ParseVec2(PyObject *o, double *x, double *y);

