#include <Python.h>
#include "capsule_helpers.h"
#include "../adapter/adapter.h"

/**
 * Implements transformation-specific Python bindings.
 * Handled via 4x4 matrices stored in PyCapsules.
 */

static void mat_capsule_destructor(PyObject *capsule) {
    void *ptr = get_capsule_pointer(capsule, "brlcad.mat");
    if (ptr) {
        free(ptr);
    }
}

PyObject* py_brlcad_create_mat(PyObject *self, PyObject *args) {
    double *mat = (double*)malloc(16 * sizeof(double));
    if (!mat) return PyErr_NoMemory();
    
    brlcad_mat_idn(mat);
    return create_capsule(mat, "brlcad.mat", mat_capsule_destructor);
}

PyObject* py_brlcad_mat_translate(PyObject *self, PyObject *args) {
    PyObject *capsule;
    double x, y, z;
    if (!PyArg_ParseTuple(args, "Oddd", &capsule, &x, &y, &z)) return NULL;

    double *mat = (double*)get_capsule_pointer(capsule, "brlcad.mat");
    if (!mat) return NULL;

    brlcad_mat_translate(mat, x, y, z);
    Py_RETURN_NONE;
}

PyObject* py_brlcad_mat_rotate_x(PyObject *self, PyObject *args) {
    PyObject *capsule;
    double angle;
    if (!PyArg_ParseTuple(args, "Od", &capsule, &angle)) return NULL;

    double *mat = (double*)get_capsule_pointer(capsule, "brlcad.mat");
    if (!mat) return NULL;

    brlcad_mat_rotate_x(mat, angle);
    Py_RETURN_NONE;
}

PyObject* py_brlcad_mat_rotate_y(PyObject *self, PyObject *args) {
    PyObject *capsule;
    double angle;
    if (!PyArg_ParseTuple(args, "Od", &capsule, &angle)) return NULL;

    double *mat = (double*)get_capsule_pointer(capsule, "brlcad.mat");
    if (!mat) return NULL;

    brlcad_mat_rotate_y(mat, angle);
    Py_RETURN_NONE;
}

PyObject* py_brlcad_mat_rotate_z(PyObject *self, PyObject *args) {
    PyObject *capsule;
    double angle;
    if (!PyArg_ParseTuple(args, "Od", &capsule, &angle)) return NULL;

    double *mat = (double*)get_capsule_pointer(capsule, "brlcad.mat");
    if (!mat) return NULL;

    brlcad_mat_rotate_z(mat, angle);
    Py_RETURN_NONE;
}

PyObject* py_brlcad_mat_scale(PyObject *self, PyObject *args) {
    PyObject *capsule;
    double factor;
    if (!PyArg_ParseTuple(args, "Od", &capsule, &factor)) return NULL;

    double *mat = (double*)get_capsule_pointer(capsule, "brlcad.mat");
    if (!mat) return NULL;

    brlcad_mat_scale(mat, factor);
    Py_RETURN_NONE;
}

/* Modifying comb_add_member to take a matrix capsule */
PyObject* py_brlcad_comb_add_member_v2(PyObject *self, PyObject *args) {
    PyObject *comb_capsule, *db_capsule, *mat_capsule;
    const char *member_name;
    
    if (!PyArg_ParseTuple(args, "OOsO", &comb_capsule, &db_capsule, &member_name, &mat_capsule)) return NULL;

    void *comb = get_capsule_pointer(comb_capsule, "brlcad.comb");
    void *db = get_capsule_pointer(db_capsule, "brlcad.db");
    double *mat = (double*)get_capsule_pointer(mat_capsule, "brlcad.mat");

    if (!comb || !db || !mat) return NULL;

    /* mk_addmember usage in adapter/comb_adapter.c needs modification for matrix */
    // For now we'll call a version that takes the matrix
    // result = brlcad_comb_add_member_with_mat(comb, db, member_name, 'u', mat);
    
    // Actually, I should update comb_adapter.c to take the matrix
    return PyErr_Format(PyExc_RuntimeError, "Not yet fully implemented for matrix pass-through");
}
