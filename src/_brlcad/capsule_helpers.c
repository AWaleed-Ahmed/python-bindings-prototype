#include <Python.h>
#include <stdio.h>
#include <string.h>
#include "capsule_helpers.h"
#include "../adapter/adapter.h"

/**
 * Implements PyCapsule infrastructure for secure BRL-CAD native pointer storage.
 *
 * This implementation allows Python to own and manage native pointers safely,
 * providing runtime type check and automatic cleanup using default destructors.
 */

/* Creates a new capsule, wrapping the native pointer as a Python object. */
PyObject* create_capsule(void *ptr, const char *name, PyCapsule_Destructor destructor) {
    if (!ptr) {
        PyErr_SetString(PyExc_RuntimeError, "Cannot create capsule for NULL pointer.");
        return NULL;
    }

    /**
     * Using PyCapsule_New to create a new capsule object.
     * The pointer is now 'owned' by Python in that Python handles the capsule's lifecycle.
     */
    return PyCapsule_New(ptr, name, destructor);
}

/* Verifies the capsule type and name, then retrieves the stored native pointer. */
void* get_capsule_pointer(PyObject *capsule, const char *expected_name) {
    /**
     * Check if the object is exactly a PyCapsule.
     */
    if (!PyCapsule_CheckExact(capsule)) {
        PyErr_SetString(PyExc_TypeError, "Value is not a PyCapsule.");
        return NULL;
    }

    /**
     * Retrieve the pointer while verifying the capsule name.
     * If the names do not match, PyCapsule_GetPointer returns NULL and sets an error.
     */
    void *ptr = PyCapsule_GetPointer(capsule, expected_name);
    if (!ptr) {
        if (!PyErr_Occurred()) {
            PyErr_SetString(PyExc_RuntimeError, "Failed to retrieve pointer from capsule");
        }
        return NULL;
    }

    return ptr;
}

/**
 * Default destructor called by Python when garbage collecting the object.
 *
 * This implementation prints a debug message to help track pointer lifecycles.
 * It now calls the native brlcad_db_close for the db capsule.
 */
void capsule_default_destructor(PyObject *capsule) {
    const char *name = PyCapsule_GetName(capsule);
    void *ptr = PyCapsule_GetPointer(capsule, name);

    /**
     * Debugging the destruction of the pointer.
     */
    printf("[pybrlcad] capsule destroyed for pointer %p (type: %s)\n", ptr, name);

    /**
     * Call BRL-CAD specific release for database capsules.
     */
    if (ptr && strcmp(name, BRLCAD_DB_CAPSULE) == 0) {
        brlcad_db_close(ptr);
    }
}
