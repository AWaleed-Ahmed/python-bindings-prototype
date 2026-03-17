#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "adapter.h"

/* BRL-CAD specific headers */
#include "vmath.h"
#include "raytrace.h"
#include "wdb.h"
#include "bu.h"

/**
 * Implements BRL-CAD transformations and attribute management.
 */

void brlcad_mat_idn(double *mat) {
    MAT_IDN(mat);
}

void brlcad_mat_translate(double *mat, double x, double y, double z) {
    mat_t m;
    MAT_IDN(m);
    m[MDX] = x;
    m[MDY] = y;
    m[MDZ] = z;
    
    mat_t res;
    bn_mat_mul(res, m, mat);
    MAT_COPY(mat, res);
}

void brlcad_mat_rotate_x(double *mat, double angle_deg) {
    mat_t m;
    double rad = angle_deg * M_PI / 180.0;
    bn_mat_angles(m, rad, 0.0, 0.0);
    
    mat_t res;
    bn_mat_mul(res, m, mat);
    MAT_COPY(mat, res);
}

void brlcad_mat_rotate_y(double *mat, double angle_deg) {
    mat_t m;
    double rad = angle_deg * M_PI / 180.0;
    bn_mat_angles(m, 0.0, rad, 0.0);
    
    mat_t res;
    bn_mat_mul(res, m, mat);
    MAT_COPY(mat, res);
}

void brlcad_mat_rotate_z(double *mat, double angle_deg) {
    mat_t m;
    double rad = angle_deg * M_PI / 180.0;
    bn_mat_angles(m, 0.0, 0.0, rad);
    
    mat_t res;
    bn_mat_mul(res, m, mat);
    MAT_COPY(mat, res);
}

void brlcad_mat_scale(double *mat, double factor) {
    mat_t m;
    MAT_IDN(m);
    m[0] = factor;
    m[5] = factor;
    m[10] = factor;
    
    mat_t res;
    bn_mat_mul(res, m, mat);
    MAT_COPY(mat, res);
}
