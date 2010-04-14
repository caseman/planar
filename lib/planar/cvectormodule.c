#include "Python.h"
#include "planar.h"

static int
Vec2_init(PlanarVec2Object *self, PyObject *args)
{
    PyObject *xarg;
    PyObject *yarg;

    assert(PlanarVec2_Check(self));
    if (PyTuple_GET_SIZE(args) != 2) {
        PyErr_SetString(PyExc_TypeError, "Vec2: wrong number of arguments");
        return -1;
    }
    xarg = PyTuple_GET_ITEM(args, 0);
    if (!PyNumber_Check(xarg)) {
        PyErr_SetString(PyExc_TypeError, "Vec2: expected number for argument one");
        return -1;
    }
    yarg = PyTuple_GET_ITEM(args, 1);
    if (!PyNumber_Check(yarg)) {
        PyErr_SetString(PyExc_TypeError, "Vec2: expected number for argument two");
        return -1;
    }
    xarg = PyNumber_Float(xarg);
    yarg = PyNumber_Float(yarg);
    if (xarg == NULL || yarg == NULL) {
        Py_XDECREF(xarg);
        Py_XDECREF(yarg);
        return -1;
    }

    self->vec.x = PyFloat_AsDouble(xarg);
    self->vec.y = PyFloat_AsDouble(yarg);
    Py_DECREF(xarg);
    Py_DECREF(yarg);
    return 0;
}

static void
Vec2_dealloc(PlanarVec2Object *self)
{
    Py_TYPE(self)->tp_free(self);
}

static PyObject *
Vec2_get_x(PlanarVec2Object *self) {
    return PyFloat_FromDouble(self->vec.x);
}

static PyObject *
Vec2_get_y(PlanarVec2Object *self) {
    return PyFloat_FromDouble(self->vec.y);
}

static PyGetSetDef Vec2_getset[] = {
    {"x", (getter)Vec2_get_x, NULL, "The horizontal coordinate.", NULL},
    {"y", (getter)Vec2_get_y, NULL, "The vertical coordinate.", NULL},
    {NULL}
};

static PyMethodDef Vec2_methods[] = {
    {NULL, NULL}
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
    0,                    /* tp_compare */
    0,                    /* tp_repr */
    0,                    /* tp_as_number */
    0,                    /* tp_as_sequence */
    0,                    /* tp_as_mapping */
    0,                    /* tp_hash */
    0,                    /* tp_call */
    0,                    /* tp_str */
    0, /* PyObject_GenericGetAttr, */                   /* tp_getattro */
    0,/* PyObject_GenericSetAttr, */                    /* tp_setattro */
    0,                    /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,   /* tp_flags */
    Vec2_doc,          /* tp_doc */
    0,                    /* tp_traverse */
    0,                    /* tp_clear */
    0,                    /* tp_richcompare */
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
    (initproc)Vec2_init,                    /* tp_init */
    PyType_GenericAlloc,        /* tp_alloc */
    0,          /* tp_new */
    PyObject_GC_Del,              /* tp_free */
};

PyDoc_STRVAR(module_doc, "Native code vector implementation");

#if PY_MAJOR_VERSION >= 3

static struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "cvector",
        module_doc,
        -1,                 /* m_size */
        NULL,               /* m_methods */
        NULL,               /* m_reload (unused) */
        NULL,               /* m_traverse */
        NULL,               /* m_clear */
        NULL                /* m_free */
};

#define INITERROR return NULL

PyObject *
PyInit_cvector(void)

#else
#define INITERROR return

void
initcvector(void)
#endif
{
#if PY_MAJOR_VERSION >= 3
    PyObject *module = PyModule_Create(&moduledef);
#else
    PyObject *module = Py_InitModule3("cvector", NULL, module_doc);
#endif

    PlanarVec2Type.tp_new = PyType_GenericNew;
    if (PyType_Ready(&PlanarVec2Type) < 0) {
        goto fail;
    }
    Py_INCREF((PyObject*)&PlanarVec2Type);
    if (PyModule_AddObject(module, "Vec2", (PyObject*)&PlanarVec2Type) < 0) {
        Py_DECREF((PyObject*)&PlanarVec2Type);
        goto fail;
    }

#if PY_MAJOR_VERSION >= 3
    return module;
#endif
fail:
    Py_DECREF(module);
    INITERROR;
}

