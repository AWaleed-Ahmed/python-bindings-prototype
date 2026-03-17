#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "adapter.h"

/* BRL-CAD specific headers */
#include "vmath.h"
#include "raytrace.h"
#include "wdb.h"
#include "bu.h"

/**
 * Implements BRL-CAD advanced primitive creation (TGC, ELL).
 */

int brlcad_create_tgc(void* wdb_handle, const char* name, 
                      double* base, double* height, 
                      double* a, double* b, 
                      double* c, double* d) {
    if (!wdb_handle || !name) return -1;
    struct rt_wdb *wdbp = (struct rt_wdb*)wdb_handle;
    
    point_t p_base;
    vect_t v_height, v_a, v_b, v_c, v_d;
    
    VMOVE(p_base, base);
    VMOVE(v_height, height);
    VMOVE(v_a, a);
    VMOVE(v_b, b);
    VMOVE(v_c, c);
    VMOVE(v_d, d);
    
    if (mk_tgc(wdbp, name, p_base, v_height, v_a, v_b, v_c, v_d) < 0) {
        fprintf(stderr, "[adapter] mk_tgc failed for %s\n", name);
        return -1;
    }
    
    printf("[adapter] Created TGC: %s\n", name);
    return 0;
}

int brlcad_create_ell(void* wdb_handle, const char* name, 
                      double* center, double* a, double* b, double* c) {
    if (!wdb_handle || !name) return -1;
    struct rt_wdb *wdbp = (struct rt_wdb*)wdb_handle;
    
    point_t p_center;
    vect_t v_a, v_b, v_c;
    
    VMOVE(p_center, center);
    VMOVE(v_a, a);
    VMOVE(v_b, b);
    VMOVE(v_c, c);
    
    if (mk_ell(wdbp, name, p_center, v_a, v_b, v_c) < 0) {
        fprintf(stderr, "[adapter] mk_ell failed for %s\n", name);
        return -1;
    }
    
    printf("[adapter] Created ELL: %s\n", name);
    return 0;
}
