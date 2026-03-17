#ifndef ADAPTER_H
#define ADAPTER_H

/**
 * Interface for BRL-CAD adapter functions.
 *
 * This layer facilitates high-level C-to-C translation for the CPython extension.
 * It abstracts BRL-CAD's complex data structures (db_i, rt_wdb) using void pointers.
 */

// Database management adapter
void* brlcad_db_open(const char *path, const char *mode);
void brlcad_db_close(void* wdb_handle);
int brlcad_list_objects(void* wdb_handle, char ***names, char ***types, int *count);

// Primitive management adapter
int brlcad_create_sphere(void* wdb_handle, const char* name, double radius);
int brlcad_get_sphere(void* wdb_handle, const char* name, double *radius, double *center);

// Advanced Primitive management adapter
int brlcad_create_tgc(void* wdb_handle, const char* name, double* base, double* height, double* a, double* b, double* c, double* d);
int brlcad_create_ell(void* wdb_handle, const char* name, double* center, double* a, double* b, double* c);

// Combination management adapter
void* brlcad_create_combination(const char *name);
int brlcad_comb_add_member(void* comb_handle, void* wdb_handle, const char* member_name, int operation, double *mat);
int brlcad_write_combination(void* wdb_handle, const char* name, void* comb_handle);
void brlcad_free_combination(void* comb_handle);

// Transformation adapter
void brlcad_mat_idn(double *mat);
void brlcad_mat_translate(double *mat, double x, double y, double z);
void brlcad_mat_rotate_x(double *mat, double angle_deg);
void brlcad_mat_rotate_y(double *mat, double angle_deg);
void brlcad_mat_rotate_z(double *mat, double angle_deg);
void brlcad_mat_scale(double *mat, double factor);

// Attribute management adapter
int brlcad_set_region(void* wdb_handle, const char* name, int region_id);
int brlcad_set_shader(void* wdb_handle, const char* name, const char *shader);
int brlcad_get_region(void* wdb_handle, const char* name, int *region_id);
int brlcad_get_shader(void* wdb_handle, const char* name, char **shader);

int brlcad_set_region_flag(void* wdb_handle, const char* name, int is_region);
int brlcad_get_region_flag(void* wdb_handle, const char* name, int *is_region);
int brlcad_set_los(void* wdb_handle, const char* name, int los);
int brlcad_get_los(void* wdb_handle, const char* name, int *los);
int brlcad_set_material_id(void* wdb_handle, const char* name, int mat_id);
int brlcad_get_material_id(void* wdb_handle, const char* name, int *mat_id);
int brlcad_set_color(void* wdb_handle, const char* name, int r, int g, int b);
int brlcad_get_color(void* wdb_handle, const char* name, int *r, int *g, int *b);

#endif /* ADAPTER_H */
