#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "adapter.h"

/* BRL-CAD specific headers */
#include "raytrace.h"
#include "wdb.h"
#include "bu.h"

/**
 * Implements BRL-CAD database connection management.
 */

void* brlcad_db_open(const char *path, const char *mode) {
    if (strcmp(mode, "w") == 0) {
        printf("[adapter] Creating BRL-CAD database: %s\n", path);
        return (void*)wdb_fopen(path);
    } else {
        printf("[adapter] Opening BRL-CAD database: %s\n", path);
        struct db_i *dbip = db_open(path, "r");
        if (dbip == DBI_NULL) {
            fprintf(stderr, "[adapter] Error opening database %s\n", path);
            return NULL;
        }
        if (db_dirbuild(dbip) < 0) {
            fprintf(stderr, "[adapter] Error building directory for %s\n", path);
            db_close(dbip);
            return NULL;
        }
        // Create an rt_wdb wrapper for consistent handle type
        return (void*)wdb_dbopen(dbip, RT_WDB_TYPE_DB_DISK);
    }
}

void brlcad_db_close(void* db_handle) {
    if (db_handle) {
        printf("[adapter] Closing BRL-CAD database handle: %p\n", db_handle);
        wdb_close((struct rt_wdb*)db_handle);
    }
}

int brlcad_list_objects(void* wdb_handle, char ***names, char ***types, int *count) {
    if (!wdb_handle) return -1;
    struct rt_wdb *wdb = (struct rt_wdb*)wdb_handle;
    struct db_i *dbip = wdb->dbip;

    int i, n;
    n = 0;
    for (i = 0; i < RT_DBNHASH; i++) {
        struct directory *dp;
        for (dp = dbip->dbi_Head[i]; dp != RT_DIR_NULL; dp = dp->d_forw) {
            n++;
        }
    }

    *count = n;
    *names = (char **)bu_calloc(n, sizeof(char *), "names array");
    *types = (char **)bu_calloc(n, sizeof(char *), "types array");

    int idx = 0;
    for (i = 0; i < RT_DBNHASH; i++) {
        struct directory *dp;
        for (dp = dbip->dbi_Head[i]; dp != RT_DIR_NULL; dp = dp->d_forw) {
            (*names)[idx] = bu_strdup(dp->d_namep);
            
            // Identify if the object is a combination or a primitive
            if (dp->d_flags & RT_DIR_COMB) {
                (*types)[idx] = bu_strdup("comb");
            } else {
                (*types)[idx] = bu_strdup("primitive");
            }
            idx++;
        }
    }

    return 0;
}
