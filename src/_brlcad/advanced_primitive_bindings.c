#include <Python.h>
#include "capsule_helpers.h"
#include "../adapter/adapter.h"

/**
 * Implements advanced primitive Python bindings for TGC and ELL.
 */

static int parse_vector3(PyObject *list, double *vec) {
    if (!PyList_Check(list) || PyList_Size(list) != 3) {
        PyErr_SetString(PyExc_TypeError, "Expected a list of 3 doubles.");
        return 0;
    }
    for (int i = 0; i < 3; i++) {
        PyObject *item = PyList_GetItem(list, i);
        if (!PyNumber_Check(item)) {
            PyErr_SetString(PyExc_TypeError, "Vector items must be numeric.");
            return 0;
        }
        vec[i] = PyFloat_AsDouble(item);
    }
    return 1;
}

PyObject* py_brlcad_create_tgc(PyObject *self, PyObject *args) {
    PyObject *db_capsule, *base_l, *height_l, *a_l, *b_l, *c_l, *d_l;
    const char *name;
    double base[3], height[3], a[3], b[3], c[3], d[3];

    if (!PyArg_ParseTuple(args, "OsOOOOOO", &db_capsule, &name, &base_l, &height_l, &a_l, &b_l, &c_l, &d_l)) return NULL;

    void *wdb = get_capsule_pointer(db_capsule, "brlcad.db");
    if (!wdb) return NULL;

    if (!parse_vector3(base_l, base) || !parse_vector3(height_l, height) || 
        !parse_vector3(a_l, a) || !parse_vector3(b_l, b) || 
        !parse_vector3(c_l, c) || !parse_vector3(d_l, d)) return NULL;

    if (brlcad_create_tgc(wdb, name, base, height, a, b, c, d) < 0) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to create TGC.");
        return NULL;
    }

    Py_RETURN_NONE;
}

PyObject* py_brlcad_create_ell(PyObject *self, PyObject *args) {
    PyObject *db_capsule, *center_l, *a_l, *b_l, *c_l;
    const char *name;
    double center[3], a[3], b[3], c[3];

    if (!PyArg_ParseTuple(args, "OsOOOO", &db_capsule, &name, &center_l, &a_l, &b_l, &c_l)) return NULL;

    void *wdb = get_capsule_pointer(db_capsule, "brlcad.db");
    if (!wdb) return NULL;

    if (!parse_vector3(center_l, center) || !parse_vector3(a_l, a) || 
        !parse_vector3(b_l, b) || !parse_vector3(c_l, c)) return NULL;

    if (brlcad_create_ell(wdb, name, center, a, b, c) < 0) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to create ELL.");
        return NULL;
    }

    Py_RETURN_NONE;
}
