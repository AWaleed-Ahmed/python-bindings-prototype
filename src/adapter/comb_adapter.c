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
 * Implements BRL-CAD combination (assembly) management using the high-level mk_ API.
 */

void* brlcad_create_combination(const char *name) {
    struct bu_list *members = (struct bu_list *)bu_calloc(1, sizeof(struct bu_list), "combination member list");
    BU_LIST_INIT(members);
    
    printf("[adapter] Created member list for combination %s\n", name);
    return (void*)members;
}

int brlcad_comb_add_member(void* comb_handle, void* wdb_handle, const char* member_name, int operation, double *mat_ptr) {
    if (!comb_handle || !member_name) return -1;
    
    struct bu_list *members = (struct bu_list*)comb_handle;
    
    /* 
     * mk_addmember adds a new member to the end of the provided bu_list.
     * Operation is typically WMOP_UNION (which is 1 in BRL-CAD Boolean ops).
     */
    mat_t mat;
    if (mat_ptr) {
        MAT_COPY(mat, mat_ptr);
    } else {
        MAT_IDN(mat);
    }
    
    if (mk_addmember(member_name, members, mat, operation) == NULL) {
        fprintf(stderr, "[adapter] mk_addmember failed for %s\n", member_name);
        return -1;
    }
    
    printf("[adapter] Added member %s to combination list\n", member_name);
    return 0;
}

int brlcad_write_combination(void* wdb_handle, const char* name, void* comb_handle) {
    if (!wdb_handle || !name || !comb_handle) return -1;
    
    struct rt_wdb *wdbp = (struct rt_wdb*)wdb_handle;
    struct bu_list *members = (struct bu_list*)comb_handle;
    
    /**
     * mk_comb writes the combination to the database.
     * It uses the members list and clears/frees it after writing.
     */
    if (mk_comb(wdbp, name, members, 
                0,      /* region_kind: 0 = group/assembly, 1 = region */
                NULL,   /* shadername */
                NULL,   /* shaderargs */
                NULL,   /* rgb */
                0,      /* id */
                0,      /* air */
                0,      /* material */
                0,      /* los */
                0,      /* inherit */
                1,      /* append_ok */
                0       /* gift_semantics */
               ) < 0) {
        fprintf(stderr, "[adapter] mk_comb failed for %s\n", name);
        return -1;
    }
    
    printf("[adapter] Wrote combination %s to database and cleared member list\n", name);
    return 0;
}

void brlcad_free_combination(void* comb_handle) {
    if (comb_handle) {
        struct bu_list *members = (struct bu_list*)comb_handle;
        /* Note: mk_comb usually frees the members, but we'll ensure cleanup */
        bu_free(members, "combination member list");
        printf("[adapter] Freed combination member list container\n");
    }
}
