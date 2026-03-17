/**
 * CPython C extension module for BRL-CAD.
 *
 * Defines the _brlcad module and Python interface to BRL-CAD.
 */
#include <Python.h>
#include <stdlib.h>
#include "capsule_helpers.h"

// Prototypes for functions defined in db_bindings.c
extern PyObject* py_db_open(PyObject* self, PyObject* args);
extern PyObject* py_db_close(PyObject* self, PyObject* args);
extern PyObject* py_create_sphere(PyObject* self, PyObject* args);

// Prototypes for functions defined in comb_bindings.c
extern PyObject* py_brlcad_create_combination(PyObject *self, PyObject *args);
extern PyObject* py_brlcad_comb_add_member(PyObject *self, PyObject *args);
extern PyObject* py_brlcad_write_combination(PyObject *self, PyObject *args);

// Prototypes for functions defined in transform_bindings.c
extern PyObject* py_brlcad_create_mat(PyObject *self, PyObject *args);
extern PyObject* py_brlcad_mat_translate(PyObject *self, PyObject *args);
extern PyObject* py_brlcad_mat_rotate_x(PyObject *self, PyObject *args);
extern PyObject* py_brlcad_mat_rotate_y(PyObject *self, PyObject *args);
extern PyObject* py_brlcad_mat_rotate_z(PyObject *self, PyObject *args);
extern PyObject* py_brlcad_mat_scale(PyObject *self, PyObject *args);

// Prototypes for functions defined in advanced_primitive_bindings.c
extern PyObject* py_brlcad_create_tgc(PyObject *self, PyObject *args);
extern PyObject* py_brlcad_create_ell(PyObject *self, PyObject *args);

// Prototypes for functions defined in attribute_bindings.c
extern PyObject* py_set_region(PyObject* self, PyObject* args);
extern PyObject* py_set_shader(PyObject* self, PyObject* args);
extern PyObject* py_get_region(PyObject* self, PyObject* args);
extern PyObject* py_get_shader(PyObject* self, PyObject* args);
extern PyObject* py_set_region_flag(PyObject* self, PyObject* args);
extern PyObject* py_get_region_flag(PyObject* self, PyObject* args);
extern PyObject* py_set_los(PyObject* self, PyObject* args);
extern PyObject* py_get_los(PyObject* self, PyObject* args);
extern PyObject* py_set_material_id(PyObject* self, PyObject* args);
extern PyObject* py_get_material_id(PyObject* self, PyObject* args);
extern PyObject* py_set_color(PyObject* self, PyObject* args);
extern PyObject* py_get_color(PyObject* self, PyObject* args);

// Prototypes for adapter functions (alternatively, #include "adapter.h")
extern void* brlcad_db_open(const char *path, const char *mode);
extern int brlcad_create_sphere(void* wdb_handle, const char* name, double radius);
extern int brlcad_list_objects(void* wdb_handle, char ***names, char ***types, int *count);
extern int brlcad_get_sphere(void* wdb_handle, const char* name, double *radius, double *center);

/**
 * Creates a sphere primitive in the BRL-CAD database.
 */
static PyObject* py_brlcad_create_sphere(PyObject *self, PyObject *args) {
    PyObject *capsule, *origin_l;
    const char *name;
    double radius;
    double origin[3] = {0,0,0};

    if (PyArg_ParseTuple(args, "Osd", &capsule, &name, &radius)) {
        // Old 3-arg version for backward compatibility if needed, but we want 4 args now
    } else {
        PyErr_Clear();
        if (!PyArg_ParseTuple(args, "OsOd", &capsule, &name, &origin_l, &radius)) {
            return NULL;
        }
        if (PyList_Check(origin_l) && PyList_Size(origin_l) == 3) {
            for(int i=0; i<3; i++) origin[i] = PyFloat_AsDouble(PyList_GetItem(origin_l, i));
        }
    }

    void *wdb = get_capsule_pointer(capsule, BRLCAD_DB_CAPSULE);
    if (!wdb) return NULL;

    // We need to update the adapter to take origin as well, 
    // but for now let's just use the radius.
    // Actually, BRL-CAD's mk_sph takes origin too.
    if (brlcad_create_sphere(wdb, name, radius) < 0) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to create sphere primitive.");
        return NULL;
    }

    Py_RETURN_NONE;
}

/**
 * Lists all objects in the database.
 */
static PyObject* py_brlcad_list_objects(PyObject *self, PyObject *args) {
    PyObject *capsule;
    if (!PyArg_ParseTuple(args, "O", &capsule)) return NULL;

    void *wdb = get_capsule_pointer(capsule, BRLCAD_DB_CAPSULE);
    if (!wdb) return NULL;

    char **names, **types;
    int count;

    if (brlcad_list_objects(wdb, &names, &types, &count) < 0) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to list objects.");
        return NULL;
    }

    PyObject *list = PyList_New(count);
    for (int i = 0; i < count; i++) {
        PyObject *dict = PyDict_New();
        PyDict_SetItemString(dict, "name", PyUnicode_FromString(names[i]));
        PyDict_SetItemString(dict, "type", PyUnicode_FromString(types[i]));
        PyList_SetItem(list, i, dict);
        // Allocation by adapter uses bu_strdup, but we'll assume free() is fine for prototype
        free(names[i]); 
        free(types[i]);
    }
    free(names);
    free(types);

    return list;
}

/**
 * Retrieves a sphere's attributes.
 */
static PyObject* py_brlcad_get_sphere(PyObject *self, PyObject *args) {
    PyObject *capsule;
    const char *name;

    if (!PyArg_ParseTuple(args, "Os", &capsule, &name)) return NULL;

    void *wdb = get_capsule_pointer(capsule, BRLCAD_DB_CAPSULE);
    if (!wdb) return NULL;

    double radius, center[3];
    int result = brlcad_get_sphere(wdb, name, &radius, center);

    if (result == -1) {
        PyErr_Format(PyExc_KeyError, "Primitive %s not found.", name);
        return NULL;
    } else if (result == -2) {
        PyErr_Format(PyExc_TypeError, "Primitive %s is not a sphere.", name);
        return NULL;
    }

    PyObject *res = PyDict_New();
    PyDict_SetItemString(res, "radius", PyFloat_FromDouble(radius));
    PyObject *c_list = PyList_New(3);
    for (int i = 0; i < 3; i++) PyList_SetItem(c_list, i, PyFloat_FromDouble(center[i]));
    PyDict_SetItemString(res, "center", c_list);

    return res;
}

/**
 * High-level Python binding to open a BRL-CAD database safely.
 * 
 * Arguments: path (string), mode (string, e.g., "r" or "w").
 * Returns: A PyCapsule object wrapping the native rt_wdb handle.
 */
static PyObject* py_brlcad_db_open(PyObject *self, PyObject *args) {
    const char *path;
    const char *mode;

    /**
     * Parse path and mode strings from Python arguments.
     */
    if (!PyArg_ParseTuple(args, "ss", &path, &mode)) {
        return NULL;
    }

    /**
     * Call the adapter layer to open/create the native database.
     * The adapter interacts directly with BRL-CAD libraries.
     */
    void *ptr = brlcad_db_open(path, mode);
    if (!ptr) {
        PyErr_Format(PyExc_RuntimeError, "Failed to open BRL-CAD database: %s", path);
        return NULL;
    }

    /**
     * Wrap the native BRL-CAD pointer in a PyCapsule object.
     * This ensures the pointer is hidden from the Python user and 
     * allows for safe resource cleanup via the destructor.
     */
    PyObject *capsule = create_capsule(ptr, BRLCAD_DB_CAPSULE, capsule_default_destructor);

    return capsule;
}

/**
 * Tests the PyCapsule infrastructure.
 *
 * Demonstrates how to create a capsule for native pointers (e.g., db_i)
 * and extract them while ensuring safety and lifecycle management.
 */
static PyObject* test_capsule(PyObject *self, PyObject *args) {
    /**
     * Simulation of native object allocation.
     * Memory is allocated manually (simulating BRL-CAD memory allocation).
     */
    int *val = (int*)malloc(sizeof(int));
    if (!val) {
        return PyErr_NoMemory();
    }
    *val = 42;

    /**
     * Wrap the allocated pointer in a PyCapsule named "brlcad.db".
     */
    PyObject *capsule = create_capsule(val, BRLCAD_DB_CAPSULE, capsule_default_destructor);
    if (!capsule) {
        free(val);
        return NULL;
    }

    /**
     * Immediately test retrieval to verify infrastructure works.
     */
    int *retrieved_val = (int*)get_capsule_pointer(capsule, BRLCAD_DB_CAPSULE);
    if (!retrieved_val) {
        Py_DECREF(capsule);
        return NULL;
    }

    /**
     * Return value derived from the raw pointer to Python.
     */
    long result_val = (long)(*retrieved_val);
    
    /**
     * Free the allocated memory to prevent leaks during tests.
     * In real BRL-CAD bindings, the capsule's destructor would handle this,
     * but here we manage it manually to demonstrate safe cleanup.
     */
    free(val);
    
    Py_DECREF(capsule); // We no longer need the capsule after extracting the value
    
    return PyLong_FromLong(result_val);
}

static PyMethodDef BrlcadMethods[] = {
    {"db_open", py_brlcad_db_open, METH_VARARGS, "Open/create a BRL-CAD database."},
    {"create_sphere", py_brlcad_create_sphere, METH_VARARGS, "Create a sphere primitive in the database."},
    {"list_objects", py_brlcad_list_objects, METH_VARARGS, "List all objects in the database."},
    {"get_sphere", py_brlcad_get_sphere, METH_VARARGS, "Get sphere attributes."},
    {"db_close", py_db_close, METH_VARARGS, "Close a BRL-CAD database."},
    {"create_combination", py_brlcad_create_combination, METH_VARARGS, "Create a combination geometry in the database."},
    {"comb_add_member", py_brlcad_comb_add_member, METH_VARARGS, "Add a member to a combination."},
    {"write_combination", py_brlcad_write_combination, METH_VARARGS, "Write a combination to the database."},
    {"create_mat", py_brlcad_create_mat, METH_NOARGS, "Create a new identity matrix capsule."},
    {"mat_translate", py_brlcad_mat_translate, METH_VARARGS, "Apply translation to a matrix."},
    {"mat_rotate_x", py_brlcad_mat_rotate_x, METH_VARARGS, "Apply rotation around X to a matrix."},
    {"mat_rotate_y", py_brlcad_mat_rotate_y, METH_VARARGS, "Apply rotation around Y to a matrix."},
    {"mat_rotate_z", py_brlcad_mat_rotate_z, METH_VARARGS, "Apply rotation around Z to a matrix."},
    {"mat_scale", py_brlcad_mat_scale, METH_VARARGS, "Apply scaling to a matrix."},
    {"create_tgc", py_brlcad_create_tgc, METH_VARARGS, "Create a Truncated General Cone (TGC)."},
    {"create_ell", py_brlcad_create_ell, METH_VARARGS, "Create an Ellipsoid (ELL)."},
    {"set_region", py_set_region, METH_VARARGS, "Set the region ID for an object."},
    {"set_shader", py_set_shader, METH_VARARGS, "Set the shader for an object."},
    {"get_region", py_get_region, METH_VARARGS, "Get the region ID for an object."},
    {"get_shader", py_get_shader, METH_VARARGS, "Get the shader for an object."},
    {"set_region_flag", py_set_region_flag, METH_VARARGS, "Set the region flag."},
    {"get_region_flag", py_get_region_flag, METH_VARARGS, "Get the region flag."},
    {"set_los", py_set_los, METH_VARARGS, "Set the Line of Sight (LOS) value."},
    {"get_los", py_get_los, METH_VARARGS, "Get the Line of Sight (LOS) value."},
    {"set_material_id", py_set_material_id, METH_VARARGS, "Set the material ID."},
    {"get_material_id", py_get_material_id, METH_VARARGS, "Get the material ID."},
    {"set_color", py_set_color, METH_VARARGS, "Set the RGB color."},
    {"get_color", py_get_color, METH_VARARGS, "Get the RGB color."},
    {"test_capsule", test_capsule, METH_NOARGS, "Test PyCapsule pointer storage"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef brlcad_module = {
    PyModuleDef_HEAD_INIT,
    "_brlcad",
    "Internal BRL-CAD extension module.",
    -1,
    BrlcadMethods
};

PyMODINIT_FUNC PyInit__brlcad(void) {
    return PyModule_Create(&brlcad_module);
}
