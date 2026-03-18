#include <stdio.h>
#include "adapter.h"

/* BRL-CAD headers */
#include "vmath.h"
#include "raytrace.h"
#include "rt/geom.h"
#include "wdb.h"

int brlcad_create_sphere(void* wdb_handle, const char* name, double radius) {
    if (!wdb_handle) {
        return 0;
    }

    struct rt_wdb *wdb = (struct rt_wdb*)wdb_handle;
    point_t center = {0, 0, 0};

    printf("[adapter] Creating sphere %s with radius %.2f\n", name, radius);

    /* mk_sph writes directly to the rt_wdb handle */
    if (mk_sph(wdb, name, center, radius) < 0) {
        fprintf(stderr, "[adapter] mk_sph failed for %s\n", name);
        return -1;
    }

    return 1;
}

int brlcad_create_box(void* wdb_handle, const char* name, double x, double y, double z) {
    if (!wdb_handle) return 0;
    struct rt_wdb *wdb = (struct rt_wdb*)wdb_handle;
    point_t min = {-x/2.0, -y/2.0, -z/2.0};
    point_t max = {x/2.0, y/2.0, z/2.0};
    printf("[adapter] Creating box %s dimensions %.2fx%.2fx%.2f\n", name, x, y, z);
    if (mk_rpp(wdb, name, min, max) < 0) return -1;
    return 1;
}

int brlcad_create_cylinder(void* wdb_handle, const char* name, double radius, double height) {
    if (!wdb_handle) return 0;
    struct rt_wdb *wdb = (struct rt_wdb*)wdb_handle;
    point_t base = {0, 0, -height/2.0};
    point_t top = {0, 0, height/2.0};
    printf("[adapter] Creating cylinder %s radius %.2f, height %.2f\n", name, radius, height);
    if (mk_rcc(wdb, name, base, top, radius) < 0) return -1;
    return 1;
}

int brlcad_get_sphere(void* wdb_handle, const char* name, double *radius, double *center) {
    if (!wdb_handle) return -1;
    struct rt_wdb *wdb = (struct rt_wdb*)wdb_handle;
    struct rt_db_internal dbi;

    struct directory *dp = db_lookup(wdb->dbip, name, LOOKUP_QUIET);
    if (dp == RT_DIR_NULL) {
        return -1;
    }

    if (rt_db_get_internal(&dbi, dp, wdb->dbip, NULL, &rt_uniresource) < 0) {
        return -1;
    }

    // Both SPH and ELL use rt_ell_internal
    if (dbi.idb_type != ID_SPH && dbi.idb_type != ID_ELL) {
        rt_db_free_internal(&dbi);
        return -2; // Not a sphere/ellipsoid
    }

    struct rt_ell_internal *ell = (struct rt_ell_internal *)dbi.idb_ptr;
    RT_ELL_CK_MAGIC(ell);

    VMOVE(center, ell->v);
    *radius = MAGNITUDE(ell->a); // For a sphere, length of axis a is the radius

    rt_db_free_internal(&dbi);
    return 0;
}

int create_combination_adapter(void* db_handle, const char* name, const char** members, int num_members) {
    printf("[adapter] Creating combination: %s with %d members.\n", name, num_members);
    return 1;
}
