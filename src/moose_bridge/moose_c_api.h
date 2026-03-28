#ifndef PYBRLCAD_MOOSE_C_API_H
#define PYBRLCAD_MOOSE_C_API_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stddef.h>

/* Opaque handles to keep C ABI stable across C++ compiler differences. */
typedef void* moose_db_handle;
typedef void* moose_comb_handle;

/* Return codes: 0 success, non-zero error. */
enum moose_status {
    MOOSE_STATUS_OK = 0,
    MOOSE_STATUS_ERROR = 1,
    MOOSE_STATUS_INVALID_ARGUMENT = 2,
    MOOSE_STATUS_NOT_FOUND = 3,
    MOOSE_STATUS_UNSUPPORTED = 4,
    MOOSE_STATUS_NOT_WRITABLE = 5,
    MOOSE_STATUS_NOT_IMPLEMENTED = 6
};

/* Database lifecycle */
int moose_db_open(const char* filename, const char* mode, moose_db_handle* out_db);
int moose_db_close(moose_db_handle db);

/* Core primitives (representative first) */
int moose_db_create_sphere(moose_db_handle db, const char* name, const double center[3], double radius);
int moose_db_create_arb8(moose_db_handle db, const char* name, const double points[8][3]);
int moose_db_create_bot(moose_db_handle db, const char* name,
                        const double* vertices_xyz, size_t vertex_count,
                        const int* faces, size_t face_count);

/* Combinations + matrix-member flow */
int moose_comb_create(const char* name, moose_comb_handle* out_comb);
int moose_comb_add_member(moose_comb_handle comb, const char* member_name, char operation, const double mat16[16]);
int moose_comb_write(moose_db_handle db, const char* name, moose_comb_handle comb);
int moose_comb_free(moose_comb_handle comb);

/* Unified read entrypoint (supported subset) */
int moose_db_get_object_json(moose_db_handle db, const char* name, char* out_json, size_t out_json_size);

/* Attributes */
int moose_db_set_attribute(moose_db_handle db, const char* object_name, const char* key, const char* value);
int moose_db_get_attribute(moose_db_handle db, const char* object_name, const char* key, char* out_value, size_t out_value_size);

/* Human-readable error for last failure in current thread/context. */
const char* moose_last_error(void);

#ifdef __cplusplus
}
#endif

#endif
