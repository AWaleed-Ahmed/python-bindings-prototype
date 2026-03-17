#include <Python.h>
#include "capsule_helpers.h"
#include "../adapter/adapter.h"

/**
 * Implements combination-specific Python bindings.
 */

/* PyCapsule and cleanup logic for combinations */
static void comb_capsule_destructor(PyObject *capsule) {
    void *ptr = get_capsule_pointer(capsule, "brlcad.comb");
    if (ptr) {
        brlcad_free_combination(ptr);
    }
}

/* Python: create_combination(name) -> Capsule(brlcad.comb) */
PyObject* py_brlcad_create_combination(PyObject *self, PyObject *args) {
    const char *name;
    if (!PyArg_ParseTuple(args, "s", &name)) return NULL;

    void *comb = brlcad_create_combination(name);
    if (!comb) return NULL;

    return create_capsule(comb, "brlcad.comb", comb_capsule_destructor);
}

/* Python: comb_add_member(comb_capsule, db_capsule, member_name, mat_capsule) */
PyObject* py_brlcad_comb_add_member(PyObject *self, PyObject *args) {
    PyObject *comb_capsule, *db_capsule, *mat_capsule = Py_None;
    const char *member_name;
    
    if (!PyArg_ParseTuple(args, "OOs|O", &comb_capsule, &db_capsule, &member_name, &mat_capsule)) return NULL;

    void *comb = get_capsule_pointer(comb_capsule, "brlcad.comb");
    void *db = get_capsule_pointer(db_capsule, "brlcad.db");
    double *mat = NULL;
    
    if (mat_capsule != Py_None) {
        mat = (double*)get_capsule_pointer(mat_capsule, "brlcad.mat");
    }

    if (!comb || !db) return NULL;

    // Use union operation ('u')
    int result = brlcad_comb_add_member(comb, db, member_name, 'u', mat);
    return PyLong_FromLong(result);
}

/* Python: write_combination(db_capsule, name, comb_capsule) */
PyObject* py_brlcad_write_combination(PyObject *self, PyObject *args) {
    PyObject *db_capsule, *comb_capsule;
    const char *name;

    if (!PyArg_ParseTuple(args, "OsO", &db_capsule, &name, &comb_capsule)) return NULL;

    void *db = get_capsule_pointer(db_capsule, "brlcad.db");
    void *comb = get_capsule_pointer(comb_capsule, "brlcad.comb");

    if (!db || !comb) return NULL;

    int result = brlcad_write_combination(db, name, comb);
    return PyLong_FromLong(result);
}
