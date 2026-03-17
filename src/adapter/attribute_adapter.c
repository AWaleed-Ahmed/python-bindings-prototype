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
 * Implements full attribute management (Region, Material, Color, LOS) for pybrlcad.
 * These functions work for both primitives and combinations by looking them up in the database.
 */

int brlcad_set_region(void* wdb_handle, const char* name, int region_id) {
    if (!wdb_handle || !name) return -1;
    struct rt_wdb *wdbp = (struct rt_wdb*)wdb_handle;
    struct db_i *dbip = wdbp->dbip;

    struct directory *dp = db_lookup(dbip, name, LOOKUP_QUIET);
    if (dp == RT_DIR_NULL) return -1;

    struct rt_db_internal intern;
    if (rt_db_get_internal(&intern, dp, dbip, NULL, &rt_uniresource) < 0) return -2;

    char buf[32];
    sprintf(buf, "%d", region_id);
    
    if (intern.idb_type == ID_COMBINATION) {
        struct rt_comb_internal *comb = (struct rt_comb_internal *)intern.idb_ptr;
        comb->region_id = region_id;
    }
    bu_avs_add(&intern.idb_avs, "region_id", buf);

    if (rt_db_put_internal(dp, dbip, &intern, &rt_uniresource) < 0) {
        rt_db_free_internal(&intern);
        return -3;
    }

    rt_db_free_internal(&intern);
    return 0;
}

int brlcad_set_shader(void* wdb_handle, const char* name, const char *shader) {
    if (!wdb_handle || !name || !shader) return -1;
    struct rt_wdb *wdbp = (struct rt_wdb*)wdb_handle;
    struct db_i *dbip = wdbp->dbip;

    struct directory *dp = db_lookup(dbip, name, LOOKUP_QUIET);
    if (dp == RT_DIR_NULL) return -1;

    struct rt_db_internal intern;
    if (rt_db_get_internal(&intern, dp, dbip, NULL, &rt_uniresource) < 0) return -2;

    if (intern.idb_type == ID_COMBINATION) {
        struct rt_comb_internal *comb = (struct rt_comb_internal *)intern.idb_ptr;
        bu_vls_strcpy(&comb->shader, shader);
    }
    bu_avs_add(&intern.idb_avs, "shader", shader);

    if (rt_db_put_internal(dp, dbip, &intern, &rt_uniresource) < 0) {
        rt_db_free_internal(&intern);
        return -3;
    }

    rt_db_free_internal(&intern);
    return 0;
}

int brlcad_get_region(void* wdb_handle, const char* name, int *region_id) {
    if (!wdb_handle || !name || !region_id) return -1;
    struct rt_wdb *wdbp = (struct rt_wdb*)wdb_handle;
    struct db_i *dbip = wdbp->dbip;

    struct directory *dp = db_lookup(dbip, name, LOOKUP_QUIET);
    if (dp == RT_DIR_NULL) return -1;

    struct rt_db_internal intern;
    if (rt_db_get_internal(&intern, dp, dbip, NULL, &rt_uniresource) < 0) return -2;

    *region_id = 0;
    if (intern.idb_type == ID_COMBINATION) {
        struct rt_comb_internal *comb = (struct rt_comb_internal *)intern.idb_ptr;
        *region_id = comb->region_id;
    } else {
        const char *val = bu_avs_get(&intern.idb_avs, "region_id");
        if (val) *region_id = atoi(val);
    }

    rt_db_free_internal(&intern);
    return 0;
}

int brlcad_get_shader(void* wdb_handle, const char* name, char **shader) {
    if (!wdb_handle || !name || !shader) return -1;
    struct rt_wdb *wdbp = (struct rt_wdb*)wdb_handle;
    struct db_i *dbip = wdbp->dbip;

    struct directory *dp = db_lookup(dbip, name, LOOKUP_QUIET);
    if (dp == RT_DIR_NULL) return -1;

    struct rt_db_internal intern;
    if (rt_db_get_internal(&intern, dp, dbip, NULL, &rt_uniresource) < 0) return -2;

    const char *s = NULL;
    if (intern.idb_type == ID_COMBINATION) {
        struct rt_comb_internal *comb = (struct rt_comb_internal *)intern.idb_ptr;
        s = bu_vls_addr(&comb->shader);
    }
    if (!s || strlen(s) == 0) s = bu_avs_get(&intern.idb_avs, "shader");

    if (s) {
        *shader = strdup(s);
    } else {
        *shader = strdup("");
    }

    rt_db_free_internal(&intern);
    return 0;
}

int brlcad_set_region_flag(void* wdb_handle, const char* name, int is_region) {
    if (!wdb_handle || !name) return -1;
    struct rt_wdb *wdbp = (struct rt_wdb*)wdb_handle;
    struct db_i *dbip = wdbp->dbip;

    struct directory *dp = db_lookup(dbip, name, LOOKUP_QUIET);
    if (dp == RT_DIR_NULL) return -1;

    struct rt_db_internal intern;
    if (rt_db_get_internal(&intern, dp, dbip, NULL, &rt_uniresource) < 0) return -2;

    if (intern.idb_type == ID_COMBINATION) {
        struct rt_comb_internal *comb = (struct rt_comb_internal *)intern.idb_ptr;
        comb->region_flag = is_region;
    }
    bu_avs_add(&intern.idb_avs, "region", is_region ? "1" : "0");
    /* Compatibility: BRL-CAD also uses is_region attribute name sometimes */
    bu_avs_add(&intern.idb_avs, "is_region", is_region ? "yes" : "no");

    if (rt_db_put_internal(dp, dbip, &intern, &rt_uniresource) < 0) {
        rt_db_free_internal(&intern);
        return -3;
    }

    rt_db_free_internal(&intern);
    return 0;
}

int brlcad_get_region_flag(void* wdb_handle, const char* name, int *is_region) {
    if (!wdb_handle || !name || !is_region) return -1;
    struct rt_wdb *wdbp = (struct rt_wdb*)wdb_handle;
    struct db_i *dbip = wdbp->dbip;

    struct directory *dp = db_lookup(dbip, name, LOOKUP_QUIET);
    if (dp == RT_DIR_NULL) return -1;

    struct rt_db_internal intern;
    if (rt_db_get_internal(&intern, dp, dbip, NULL, &rt_uniresource) < 0) return -2;

    *is_region = 0;
    if (intern.idb_type == ID_COMBINATION) {
        struct rt_comb_internal *comb = (struct rt_comb_internal *)intern.idb_ptr;
        *is_region = comb->region_flag;
    } else {
        const char *val = bu_avs_get(&intern.idb_avs, "region");
        if (val && (val[0] == '1' || val[0] == 'y' || val[0] == 'Y' || val[0] == 't' || val[0] == 'T')) {
            *is_region = 1;
        } else {
            val = bu_avs_get(&intern.idb_avs, "is_region");
            if (val && (val[0] == '1' || val[0] == 'y' || val[0] == 'Y' || val[0] == 't' || val[0] == 'T')) {
                *is_region = 1;
            }
        }
    }

    rt_db_free_internal(&intern);
    return 0;
}

int brlcad_set_los(void* wdb_handle, const char* name, int los) {
    if (!wdb_handle || !name) return -1;
    struct rt_wdb *wdbp = (struct rt_wdb*)wdb_handle;
    struct db_i *dbip = wdbp->dbip;

    struct directory *dp = db_lookup(dbip, name, LOOKUP_QUIET);
    if (dp == RT_DIR_NULL) return -1;

    struct rt_db_internal intern;
    if (rt_db_get_internal(&intern, dp, dbip, NULL, &rt_uniresource) < 0) return -2;

    char buf[32];
    sprintf(buf, "%d", los);
    
    if (intern.idb_type == ID_COMBINATION) {
        struct rt_comb_internal *comb = (struct rt_comb_internal *)intern.idb_ptr;
        comb->los = los;
    }
    bu_avs_add(&intern.idb_avs, "los", buf);

    if (rt_db_put_internal(dp, dbip, &intern, &rt_uniresource) < 0) {
        rt_db_free_internal(&intern);
        return -3;
    }

    rt_db_free_internal(&intern);
    return 0;
}

int brlcad_get_los(void* wdb_handle, const char* name, int *los) {
    if (!wdb_handle || !name || !los) return -1;
    struct rt_wdb *wdbp = (struct rt_wdb*)wdb_handle;
    struct db_i *dbip = wdbp->dbip;

    struct directory *dp = db_lookup(dbip, name, LOOKUP_QUIET);
    if (dp == RT_DIR_NULL) return -1;

    struct rt_db_internal intern;
    if (rt_db_get_internal(&intern, dp, dbip, NULL, &rt_uniresource) < 0) return -2;

    *los = 0;
    if (intern.idb_type == ID_COMBINATION) {
        struct rt_comb_internal *comb = (struct rt_comb_internal *)intern.idb_ptr;
        *los = comb->los;
    } else {
        const char *val = bu_avs_get(&intern.idb_avs, "los");
        if (val) *los = atoi(val);
    }

    rt_db_free_internal(&intern);
    return 0;
}

int brlcad_set_material_id(void* wdb_handle, const char* name, int mat_id) {
    if (!wdb_handle || !name) return -1;
    struct rt_wdb *wdbp = (struct rt_wdb*)wdb_handle;
    struct db_i *dbip = wdbp->dbip;

    struct directory *dp = db_lookup(dbip, name, LOOKUP_QUIET);
    if (dp == RT_DIR_NULL) return -1;

    struct rt_db_internal intern;
    if (rt_db_get_internal(&intern, dp, dbip, NULL, &rt_uniresource) < 0) return -2;

    char buf[32];
    sprintf(buf, "%d", mat_id);
    
    bu_avs_add(&intern.idb_avs, "material_id", buf);

    if (rt_db_put_internal(dp, dbip, &intern, &rt_uniresource) < 0) {
        rt_db_free_internal(&intern);
        return -3;
    }

    rt_db_free_internal(&intern);
    return 0;
}

int brlcad_get_material_id(void* wdb_handle, const char* name, int *mat_id) {
    if (!wdb_handle || !name || !mat_id) return -1;
    struct rt_wdb *wdbp = (struct rt_wdb*)wdb_handle;
    struct db_i *dbip = wdbp->dbip;

    struct directory *dp = db_lookup(dbip, name, LOOKUP_QUIET);
    if (dp == RT_DIR_NULL) return -1;

    struct rt_db_internal intern;
    if (rt_db_get_internal(&intern, dp, dbip, NULL, &rt_uniresource) < 0) return -2;

    const char *val = bu_avs_get(&intern.idb_avs, "material_id");
    *mat_id = val ? atoi(val) : 0;

    rt_db_free_internal(&intern);
    return 0;
}

int brlcad_set_color(void* wdb_handle, const char* name, int r, int g, int b) {
    if (!wdb_handle || !name) return -1;
    struct rt_wdb *wdbp = (struct rt_wdb*)wdb_handle;
    struct db_i *dbip = wdbp->dbip;

    struct directory *dp = db_lookup(dbip, name, LOOKUP_QUIET);
    if (dp == RT_DIR_NULL) return -1;

    struct rt_db_internal intern;
    if (rt_db_get_internal(&intern, dp, dbip, NULL, &rt_uniresource) < 0) return -2;

    char buf[64];
    sprintf(buf, "%d/%d/%d", r, g, b);
    
    if (intern.idb_type == ID_COMBINATION) {
        struct rt_comb_internal *comb = (struct rt_comb_internal *)intern.idb_ptr;
        comb->rgb[0] = r;
        comb->rgb[1] = g;
        comb->rgb[2] = b;
    }
    bu_avs_add(&intern.idb_avs, "color", buf);

    if (rt_db_put_internal(dp, dbip, &intern, &rt_uniresource) < 0) {
        rt_db_free_internal(&intern);
        return -3;
    }

    rt_db_free_internal(&intern);
    return 0;
}

int brlcad_get_color(void* wdb_handle, const char* name, int *r, int *g, int *b) {
    if (!wdb_handle || !name || !r || !g || !b) return -1;
    struct rt_wdb *wdbp = (struct rt_wdb*)wdb_handle;
    struct db_i *dbip = wdbp->dbip;

    struct directory *dp = db_lookup(dbip, name, LOOKUP_QUIET);
    if (dp == RT_DIR_NULL) return -1;

    struct rt_db_internal intern;
    if (rt_db_get_internal(&intern, dp, dbip, NULL, &rt_uniresource) < 0) return -2;

    *r = *g = *b = 0;
    const char *val = bu_avs_get(&intern.idb_avs, "color");
    if (val) {
        sscanf(val, "%d/%d/%d", r, g, b);
    } else if (intern.idb_type == ID_COMBINATION) {
        struct rt_comb_internal *comb = (struct rt_comb_internal *)intern.idb_ptr;
        *r = comb->rgb[0];
        *g = comb->rgb[1];
        *b = comb->rgb[2];
    }

    rt_db_free_internal(&intern);
    return 0;
}
