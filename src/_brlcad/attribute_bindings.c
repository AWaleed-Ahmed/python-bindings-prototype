#include <Python.h>
#include "capsule_helpers.h"
#include "../adapter/adapter.h"

/**
 * Implementation of Python attribute bindings in C for Stage 10.
 */

PyObject* py_set_region(PyObject* self, PyObject* args) {
    PyObject* capsule;
    const char* name;
    int region_id;
    if (!PyArg_ParseTuple(args, "Osi", &capsule, &name, &region_id)) return NULL;
    void* db_handle = get_capsule_pointer(capsule, BRLCAD_DB_CAPSULE);
    if (!db_handle) { PyErr_SetString(PyExc_ValueError, "Invalid database capsule"); return NULL; }
    if (brlcad_set_region(db_handle, name, region_id) < 0) { PyErr_SetString(PyExc_RuntimeError, "Failed to set region_id"); return NULL; }
    Py_RETURN_NONE;
}

PyObject* py_get_region(PyObject* self, PyObject* args) {
    PyObject* capsule;
    const char* name;
    int region_id = 0;
    if (!PyArg_ParseTuple(args, "Os", &capsule, &name)) return NULL;
    void* db_handle = get_capsule_pointer(capsule, BRLCAD_DB_CAPSULE);
    if (!db_handle) { PyErr_SetString(PyExc_ValueError, "Invalid database capsule"); return NULL; }
    if (brlcad_get_region(db_handle, name, &region_id) < 0) { PyErr_SetString(PyExc_RuntimeError, "Failed to get region_id"); return NULL; }
    return PyLong_FromLong(region_id);
}

PyObject* py_set_shader(PyObject* self, PyObject* args) {
    PyObject* capsule;
    const char* name;
    const char* shader;
    if (!PyArg_ParseTuple(args, "Oss", &capsule, &name, &shader)) return NULL;
    void* db_handle = get_capsule_pointer(capsule, BRLCAD_DB_CAPSULE);
    if (!db_handle) { PyErr_SetString(PyExc_ValueError, "Invalid database capsule"); return NULL; }
    if (brlcad_set_shader(db_handle, name, shader) < 0) { PyErr_SetString(PyExc_RuntimeError, "Failed to set shader"); return NULL; }
    Py_RETURN_NONE;
}

PyObject* py_get_shader(PyObject* self, PyObject* args) {
    PyObject* capsule;
    const char* name;
    char* shader = NULL;
    if (!PyArg_ParseTuple(args, "Os", &capsule, &name)) return NULL;
    void* db_handle = get_capsule_pointer(capsule, BRLCAD_DB_CAPSULE);
    if (!db_handle) { PyErr_SetString(PyExc_ValueError, "Invalid database capsule"); return NULL; }
    if (brlcad_get_shader(db_handle, name, &shader) < 0) { PyErr_SetString(PyExc_RuntimeError, "Failed to get shader"); return NULL; }
    PyObject* py_shader = PyUnicode_FromString(shader ? shader : "");
    if (shader) free(shader);
    return py_shader;
}

PyObject* py_set_region_flag(PyObject* self, PyObject* args) {
    PyObject* capsule;
    const char* name;
    int flag;
    if (!PyArg_ParseTuple(args, "Osi", &capsule, &name, &flag)) return NULL;
    void* db_handle = get_capsule_pointer(capsule, BRLCAD_DB_CAPSULE);
    if (brlcad_set_region_flag(db_handle, name, flag) < 0) { PyErr_SetString(PyExc_RuntimeError, "Failed to set region flag"); return NULL; }
    Py_RETURN_NONE;
}

PyObject* py_get_region_flag(PyObject* self, PyObject* args) {
    PyObject* capsule;
    const char* name;
    int flag = 0;
    if (!PyArg_ParseTuple(args, "Os", &capsule, &name)) return NULL;
    void* db_handle = get_capsule_pointer(capsule, BRLCAD_DB_CAPSULE);
    if (brlcad_get_region_flag(db_handle, name, &flag) < 0) { PyErr_SetString(PyExc_RuntimeError, "Failed to get region flag"); return NULL; }
    return PyLong_FromLong(flag);
}

PyObject* py_set_los(PyObject* self, PyObject* args) {
    PyObject* capsule;
    const char* name;
    int los;
    if (!PyArg_ParseTuple(args, "Osi", &capsule, &name, &los)) return NULL;
    void* db_handle = get_capsule_pointer(capsule, BRLCAD_DB_CAPSULE);
    if (brlcad_set_los(db_handle, name, los) < 0) { PyErr_SetString(PyExc_RuntimeError, "Failed to set los"); return NULL; }
    Py_RETURN_NONE;
}

PyObject* py_get_los(PyObject* self, PyObject* args) {
    PyObject* capsule;
    const char* name;
    int los = 0;
    if (!PyArg_ParseTuple(args, "Os", &capsule, &name)) return NULL;
    void* db_handle = get_capsule_pointer(capsule, BRLCAD_DB_CAPSULE);
    if (brlcad_get_los(db_handle, name, &los) < 0) { PyErr_SetString(PyExc_RuntimeError, "Failed to get los"); return NULL; }
    return PyLong_FromLong(los);
}

PyObject* py_set_material_id(PyObject* self, PyObject* args) {
    PyObject* capsule;
    const char* name;
    int mat_id;
    if (!PyArg_ParseTuple(args, "Osi", &capsule, &name, &mat_id)) return NULL;
    void* db_handle = get_capsule_pointer(capsule, BRLCAD_DB_CAPSULE);
    if (brlcad_set_material_id(db_handle, name, mat_id) < 0) { PyErr_SetString(PyExc_RuntimeError, "Failed to set material_id"); return NULL; }
    Py_RETURN_NONE;
}

PyObject* py_get_material_id(PyObject* self, PyObject* args) {
    PyObject* capsule;
    const char* name;
    int mat_id = 0;
    if (!PyArg_ParseTuple(args, "Os", &capsule, &name)) return NULL;
    void* db_handle = get_capsule_pointer(capsule, BRLCAD_DB_CAPSULE);
    if (brlcad_get_material_id(db_handle, name, &mat_id) < 0) { PyErr_SetString(PyExc_RuntimeError, "Failed to get material_id"); return NULL; }
    return PyLong_FromLong(mat_id);
}

PyObject* py_set_color(PyObject* self, PyObject* args) {
    PyObject* capsule;
    const char* name;
    int r, g, b;
    if (!PyArg_ParseTuple(args, "Osiii", &capsule, &name, &r, &g, &b)) return NULL;
    void* db_handle = get_capsule_pointer(capsule, BRLCAD_DB_CAPSULE);
    if (brlcad_set_color(db_handle, name, r, g, b) < 0) { PyErr_SetString(PyExc_RuntimeError, "Failed to set color"); return NULL; }
    Py_RETURN_NONE;
}

PyObject* py_get_color(PyObject* self, PyObject* args) {
    PyObject* capsule;
    const char* name;
    int r = 0, g = 0, b = 0;
    if (!PyArg_ParseTuple(args, "Os", &capsule, &name)) return NULL;
    void* db_handle = get_capsule_pointer(capsule, BRLCAD_DB_CAPSULE);
    if (brlcad_get_color(db_handle, name, &r, &g, &b) < 0) { PyErr_SetString(PyExc_RuntimeError, "Failed to get color"); return NULL; }
    return Py_BuildValue("(iii)", r, g, b);
}
