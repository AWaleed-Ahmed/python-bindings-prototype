#ifndef CAPSULE_HELPERS_H
#define CAPSULE_HELPERS_H

#include <Python.h>

/**
 * Capsule constants for BRL-CAD native pointers.
 * These names are used for runtime type checking when extracting pointers
 * from PyCapsule objects.
 */
#define BRLCAD_DB_CAPSULE "brlcad.db"
#define BRLCAD_WDB_CAPSULE "brlcad.wdb"

/**
 * Capsule helper utilities to securely wrap native BRL-CAD objects (db_i, wdb, etc.).
 *
 * PyCapsule is used to safely store native BRL-CAD pointers in Python objects.
 * The capsule name acts as a runtime type check to ensure the correct pointer type is retrieved.
 * The destructor is called automatically when Python garbage collects the object,
 * providing a hook for closing BRL-CAD database handles or freeing resources.
 */

/* Wraps a raw pointer in a PyCapsule object with a specific name and destructor. */
PyObject* create_capsule(void *ptr, const char *name, PyCapsule_Destructor destructor);

/* Safely retrieves the native pointer from a PyCapsule object, verifying the name matches. */
void* get_capsule_pointer(PyObject *capsule, const char *expected_name);

/* Default cleanup/debug destructor for capsules. */
void capsule_default_destructor(PyObject *capsule);

#endif /* CAPSULE_HELPERS_H */
