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
#include "planar.h"

double PLANAR_EPSILON = 1e-5;
double PLANAR_EPSILON2 = 1e-5 * 1e-5;

static PyObject *
_set_epsilon_func(PyObject *self, PyObject *epsilon)
{
    epsilon = PyObject_ToFloat(epsilon);
    if (epsilon == NULL) {
        return NULL;
    }

    PLANAR_EPSILON = PyFloat_AS_DOUBLE(epsilon);
    PLANAR_EPSILON2 = PLANAR_EPSILON * PLANAR_EPSILON;
    Py_DECREF(epsilon);
    Py_INCREF(Py_None);
    return Py_None;
}

PyObject *PlanarTransformNotInvertibleError;

static PyMethodDef module_functions[] = {
    {"_set_epsilon", (PyCFunction) _set_epsilon_func, METH_O,
     "PRIVATE: Set epsilon value used by C extension"},
    {NULL}
};

PyDoc_STRVAR(module_doc, "Planar native code classes");

#if PY_MAJOR_VERSION >= 3

static struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "cvector",
        module_doc,
        -1,                 /* m_size */
        module_functions,   /* m_methods */
        NULL,               /* m_reload (unused) */
        NULL,               /* m_traverse */
        NULL,               /* m_clear */
        NULL                /* m_free */
};

#define INITERROR return NULL

PyObject *
PyInit_c(void)

#else
#define INITERROR return

void
initc(void)
#endif
{
#if PY_MAJOR_VERSION >= 3
    PyObject *module = PyModule_Create(&moduledef);
#else
    PyObject *module = Py_InitModule3(
        "c", module_functions, module_doc);
#endif
    Py_INCREF((PyObject *)&PlanarVec2Type);
    Py_INCREF((PyObject *)&PlanarAffineType);

    PlanarVec2Type.tp_new = PyType_GenericNew;
    if (PyType_Ready(&PlanarVec2Type) < 0) {
        goto fail;
    }
    if (PyModule_AddObject(
        module, "Vec2", (PyObject *)&PlanarVec2Type) < 0) {
        goto fail;
    }

    PlanarAffineType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&PlanarAffineType) < 0) {
        goto fail;
    }
    if (PyModule_AddObject(
        module, "Affine", (PyObject *)&PlanarAffineType) < 0) {
        goto fail;
    }

	PlanarTransformNotInvertibleError = PyErr_NewException(
		"planar.TransformNotInvertibleError", NULL, NULL);
	if (PlanarTransformNotInvertibleError == NULL) {
		goto fail;
	}
    if (PyModule_AddObject(
        module, "TransformNotInvertibleError", 
		PlanarTransformNotInvertibleError) < 0) {
        goto fail;
    }
#if PY_MAJOR_VERSION >= 3
    return module;
#else
    return;
#endif
fail:
    Py_DECREF((PyObject *)&PlanarVec2Type);
    Py_DECREF((PyObject *)&PlanarAffineType);
    Py_DECREF(module);
    INITERROR;
}

/* vim: ai ts=4 sts=4 et sw=4 tw=78 */

