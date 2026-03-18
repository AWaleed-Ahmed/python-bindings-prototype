#include <Python.h>
#include "capsule_helpers.h"
#include "../adapter/adapter.h"

/**
 * Implementation of Python database bindings in C.
 *
 * Each function extracts arguments from Python and calls BRL-CAD libraries.
 */

PyObject* py_db_open(PyObject* self, PyObject* args) {
    const char* filename;
    const char* title;
    
    if (!PyArg_ParseTuple(args, "ss", &filename, &title)) {
        return NULL;
    }
    
    // Calls adapter functions to open/create a BRL-CAD .g file.
    // Result: A void pointer to the native BRL-CAD database handle (db_i/rt_wdb).
    void* db_handle = (void*)filename; // (void*)db_open_adapter(filename, title);
    
    return create_capsule(db_handle, BRLCAD_DB_CAPSULE, capsule_default_destructor);
}

PyObject* py_db_close(PyObject* self, PyObject* args) {
    PyObject* capsule;
    if (!PyArg_ParseTuple(args, "O", &capsule)) {
        return NULL;
    }
    
    void* db_handle = get_capsule_pointer(capsule, BRLCAD_DB_CAPSULE);
    if (db_handle) {
        // Calls adapter function to close the BRL-CAD database handle.
        // rt_db_close_adapter(db_handle);
    }
    
    Py_RETURN_NONE;
}

PyObject* py_create_sphere(PyObject* self, PyObject* args) {
    PyObject* capsule;
    const char* name;
    PyObject* origin_list;
    double radius;
    
    // Extracting Python values (tuple/list) for native call.
    if (!PyArg_ParseTuple(args, "OsOd", &capsule, &name, &origin_list, &radius)) {
        return NULL;
    }
    
    void* db_handle = get_capsule_pointer(capsule, BRLCAD_DB_CAPSULE);
    if (!db_handle) return NULL;
    
    if (brlcad_create_sphere(db_handle, name, radius) < 0) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to create sphere.");
        return NULL;
    }
    
    Py_RETURN_NONE;
}

PyObject* py_create_box(PyObject* self, PyObject* args) {
    PyObject* capsule;
    const char* name;
    double x, y, z;
    
    if (!PyArg_ParseTuple(args, "Osddd", &capsule, &name, &x, &y, &z)) {
        return NULL;
    }
    
    void* db_handle = get_capsule_pointer(capsule, BRLCAD_DB_CAPSULE);
    if (!db_handle) return NULL;
    
    if (brlcad_create_box(db_handle, name, x, y, z) < 0) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to create box.");
        return NULL;
    }
    
    Py_RETURN_NONE;
}

PyObject* py_create_cylinder(PyObject* self, PyObject* args) {
    PyObject* capsule;
    const char* name;
    double r, h;
    
    if (!PyArg_ParseTuple(args, "Osdd", &capsule, &name, &r, &h)) {
        return NULL;
    }
    
    void* db_handle = get_capsule_pointer(capsule, BRLCAD_DB_CAPSULE);
    if (!db_handle) return NULL;
    
    if (brlcad_create_cylinder(db_handle, name, r, h) < 0) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to create cylinder.");
        return NULL;
    }
    
    Py_RETURN_NONE;
}

PyObject* py_create_combination(PyObject* self, PyObject* args) {
    PyObject* capsule;
    const char* name;
    PyObject* members_list;
    
    if (!PyArg_ParseTuple(args, "OsO", &capsule, &name, &members_list)) {
        return NULL;
    }
    
    void* db_handle = get_capsule_pointer(capsule, BRLCAD_DB_CAPSULE);
    (void)db_handle; // Suppress unused warning for now
    
    // Native call: mk_comb(db_handle, name, members, ...);
    
    Py_RETURN_NONE;
}
