#include "moose_c_api.h"

/*
 * Stable C ABI bridge for BRL-CAD/MOOSE (C++ backend).
 * Python should bind to this C layer, not to C++ symbols directly.
 */

#include <brlcad/vector.h>
#include <brlcad/Database/ConstDatabase.h>
#include <brlcad/Database/Database.h>
#include <brlcad/Database/FileDatabase.h>
#include <brlcad/Database/MemoryDatabase.h>
#include <brlcad/Database/Sphere.h>
#include <brlcad/Database/Arb8.h>
#include <brlcad/Database/BagOfTriangles.h>
#include <brlcad/Database/Combination.h>

#include <array>
#include <cstring>
#include <sstream>
#include <string>
#include <vector>

static std::string g_last_error = "ok";

namespace {
enum class DbKind {
    ReadOnly,
    WritableFile,
    InMemory
};

struct DbHandle {
    DbKind kind;
    BRLCAD::ConstDatabase* ro;
    BRLCAD::Database* rw;
};

struct CombMember {
    std::string name;
    char op;
    bool has_matrix;
    std::array<double, 16> matrix;
};

struct CombHandle {
    std::string name;
    std::vector<CombMember> members;
};

static int fail(int status, const char* msg) {
    g_last_error = (msg ? msg : "unknown error");
    return status;
}

static BRLCAD::ConstDatabase* as_const_db(DbHandle* h) {
    if (!h) return nullptr;
    if (h->kind == DbKind::ReadOnly) return h->ro;
    return h->rw;
}

static BRLCAD::Database* as_rw_db(DbHandle* h) {
    if (!h) return nullptr;
    if (h->kind == DbKind::ReadOnly) return nullptr;
    return h->rw;
}

static std::string json_escape(const char* s) {
    std::string out;
    if (!s) return out;
    while (*s) {
        char c = *s++;
        switch (c) {
            case '"': out += "\\\""; break;
            case '\\': out += "\\\\"; break;
            case '\n': out += "\\n"; break;
            case '\r': out += "\\r"; break;
            case '\t': out += "\\t"; break;
            default: out += c; break;
        }
    }
    return out;
}

static BRLCAD::Combination::TreeNode::Operator map_op(char op) {
    switch (op) {
        case '-': return BRLCAD::Combination::TreeNode::Operator::Subtraction;
        case '+': return BRLCAD::Combination::TreeNode::Operator::Intersection;
        case 'u':
        case 'U':
        default: return BRLCAD::Combination::TreeNode::Operator::Union;
    }
}
}  // namespace

int moose_db_open(const char* filename, const char* mode, moose_db_handle* out_db) {
    if (!out_db) {
        return fail(MOOSE_STATUS_INVALID_ARGUMENT, "out_db must not be NULL");
    }

    const char* m = mode ? mode : "w";
    DbHandle* handle = new DbHandle();
    handle->ro = nullptr;
    handle->rw = nullptr;

    if (std::strcmp(m, "r") == 0 || std::strcmp(m, "ro") == 0 || std::strcmp(m, "read") == 0) {
        BRLCAD::ConstDatabase* db = new BRLCAD::ConstDatabase();
        if (!filename || !db->Load(filename)) {
            delete db;
            delete handle;
            return fail(MOOSE_STATUS_ERROR, "failed to load read-only database");
        }
        handle->kind = DbKind::ReadOnly;
        handle->ro = db;
    } else if (std::strcmp(m, "memory") == 0 || std::strcmp(m, "inmemory") == 0 || std::strcmp(m, "mem") == 0) {
        BRLCAD::MemoryDatabase* db = new BRLCAD::MemoryDatabase();
        if (filename && filename[0] != '\0') {
            (void)db->Load(filename);
        }
        handle->kind = DbKind::InMemory;
        handle->rw = db;
    } else {
        BRLCAD::FileDatabase* db = new BRLCAD::FileDatabase();
        if (!filename || !db->Load(filename)) {
            delete db;
            delete handle;
            return fail(MOOSE_STATUS_ERROR, "failed to open writable file database");
        }
        handle->kind = DbKind::WritableFile;
        handle->rw = db;
    }

    *out_db = reinterpret_cast<moose_db_handle>(handle);
    g_last_error = "ok";
    return MOOSE_STATUS_OK;
}

int moose_db_close(moose_db_handle db) {
    DbHandle* h = reinterpret_cast<DbHandle*>(db);
    if (!h) return MOOSE_STATUS_OK;
    if (h->ro) delete h->ro;
    if (h->rw) delete h->rw;
    delete h;
    return MOOSE_STATUS_OK;
}

int moose_db_create_sphere(moose_db_handle db, const char* name, const double center[3], double radius) {
    DbHandle* h = reinterpret_cast<DbHandle*>(db);
    BRLCAD::Database* rw = as_rw_db(h);
    if (!rw) return fail(MOOSE_STATUS_NOT_WRITABLE, "database is not writable");
    if (!name || !center) return fail(MOOSE_STATUS_INVALID_ARGUMENT, "name/center must not be NULL");

    BRLCAD::Sphere sph(BRLCAD::Vector3D(center[0], center[1], center[2]), radius);
    sph.SetName(name);
    if (!rw->Add(sph)) {
        return fail(MOOSE_STATUS_ERROR, "failed to add sphere");
    }
    g_last_error = "ok";
    return MOOSE_STATUS_OK;
}

int moose_db_create_arb8(moose_db_handle db, const char* name, const double points[8][3]) {
    DbHandle* h = reinterpret_cast<DbHandle*>(db);
    BRLCAD::Database* rw = as_rw_db(h);
    if (!rw) return fail(MOOSE_STATUS_NOT_WRITABLE, "database is not writable");
    if (!name || !points) return fail(MOOSE_STATUS_INVALID_ARGUMENT, "name/points must not be NULL");

    BRLCAD::Arb8 arb(
        BRLCAD::Vector3D(points[0][0], points[0][1], points[0][2]),
        BRLCAD::Vector3D(points[1][0], points[1][1], points[1][2]),
        BRLCAD::Vector3D(points[2][0], points[2][1], points[2][2]),
        BRLCAD::Vector3D(points[3][0], points[3][1], points[3][2]),
        BRLCAD::Vector3D(points[4][0], points[4][1], points[4][2]),
        BRLCAD::Vector3D(points[5][0], points[5][1], points[5][2]),
        BRLCAD::Vector3D(points[6][0], points[6][1], points[6][2]),
        BRLCAD::Vector3D(points[7][0], points[7][1], points[7][2])
    );
    arb.SetName(name);
    if (!rw->Add(arb)) {
        return fail(MOOSE_STATUS_ERROR, "failed to add arb8");
    }
    g_last_error = "ok";
    return MOOSE_STATUS_OK;
}

int moose_db_create_bot(moose_db_handle db, const char* name,
                        const double* vertices_xyz, size_t vertex_count,
                        const int* faces, size_t face_count) {
    DbHandle* h = reinterpret_cast<DbHandle*>(db);
    BRLCAD::Database* rw = as_rw_db(h);
    if (!rw) return fail(MOOSE_STATUS_NOT_WRITABLE, "database is not writable");
    if (!name || !vertices_xyz || !faces) return fail(MOOSE_STATUS_INVALID_ARGUMENT, "name/vertices/faces must not be NULL");
    if (vertex_count == 0 || face_count == 0) return fail(MOOSE_STATUS_INVALID_ARGUMENT, "vertex_count and face_count must be > 0");

    BRLCAD::BagOfTriangles bot;
    bot.SetName(name);
    for (size_t i = 0; i < face_count; ++i) {
        int i0 = faces[i * 3 + 0];
        int i1 = faces[i * 3 + 1];
        int i2 = faces[i * 3 + 2];
        if (i0 < 0 || i1 < 0 || i2 < 0 ||
            static_cast<size_t>(i0) >= vertex_count ||
            static_cast<size_t>(i1) >= vertex_count ||
            static_cast<size_t>(i2) >= vertex_count) {
            return fail(MOOSE_STATUS_INVALID_ARGUMENT, "face index out of range");
        }
        BRLCAD::Vector3D p0(vertices_xyz[i0 * 3 + 0], vertices_xyz[i0 * 3 + 1], vertices_xyz[i0 * 3 + 2]);
        BRLCAD::Vector3D p1(vertices_xyz[i1 * 3 + 0], vertices_xyz[i1 * 3 + 1], vertices_xyz[i1 * 3 + 2]);
        BRLCAD::Vector3D p2(vertices_xyz[i2 * 3 + 0], vertices_xyz[i2 * 3 + 1], vertices_xyz[i2 * 3 + 2]);
        bot.AddFace(p0, p1, p2);
    }

    if (!rw->Add(bot)) {
        return fail(MOOSE_STATUS_ERROR, "failed to add bag of triangles");
    }
    g_last_error = "ok";
    return MOOSE_STATUS_OK;
}

int moose_comb_create(const char* name, moose_comb_handle* out_comb) {
    if (!out_comb) {
        return fail(MOOSE_STATUS_INVALID_ARGUMENT, "out_comb must not be NULL");
    }
    CombHandle* ch = new CombHandle();
    ch->name = (name ? name : "");
    *out_comb = reinterpret_cast<moose_comb_handle>(ch);
    g_last_error = "ok";
    return MOOSE_STATUS_OK;
}

int moose_comb_add_member(moose_comb_handle comb,
     const char* member_name, char operation,
    const double mat16[16]) {
    CombHandle* ch = reinterpret_cast<CombHandle*>(comb);
    if (!ch || !member_name) return fail(MOOSE_STATUS_INVALID_ARGUMENT,
         "comb/member_name must not be NULL");
    CombMember m;
    m.name = member_name;
    m.op = operation;
    m.has_matrix = (mat16 != nullptr);
    if (mat16) {
        for (size_t i = 0; i < 16; ++i) m.matrix[i] = mat16[i];
    }
    ch->members.push_back(m);
    g_last_error = "ok";
    return MOOSE_STATUS_OK;
}

int moose_comb_write(moose_db_handle db, const char* name, moose_comb_handle comb) {
    DbHandle* h = reinterpret_cast<DbHandle*>(db);
    BRLCAD::Database* rw = as_rw_db(h);
    CombHandle* ch = reinterpret_cast<CombHandle*>(comb);
    if (!rw) return fail(MOOSE_STATUS_NOT_WRITABLE, "database is not writable");
    if (!ch) return fail(MOOSE_STATUS_INVALID_ARGUMENT, "comb must not be NULL");

    const char* comb_name = name;
    if ((!comb_name || comb_name[0] == '\0') && !ch->name.empty()) {
        comb_name = ch->name.c_str();
    }
    if (!comb_name || comb_name[0] == '\0') {
        return fail(MOOSE_STATUS_INVALID_ARGUMENT, "combination name is required");
    }

    BRLCAD::Combination c;
    c.SetName(comb_name);
    if (ch->members.empty()) {
        return fail(MOOSE_STATUS_INVALID_ARGUMENT, "combination has no members");
    }

    c.AddLeaf(ch->members[0].name.c_str());
    if (ch->members[0].has_matrix) {
        c.Tree().SetMatrix(ch->members[0].matrix.data());
    }

    BRLCAD::Combination::TreeNode tree = c.Tree();
    for (size_t i = 1; i < ch->members.size(); ++i) {
        tree = tree.Apply(map_op(ch->members[i].op), ch->members[i].name.c_str());
        if (ch->members[i].has_matrix) {
            BRLCAD::Combination::TreeNode right = tree.RightOperand();
            if (right) {
                right.SetMatrix(ch->members[i].matrix.data());
            }
        }
    }

    if (!rw->Add(c)) {
        return fail(MOOSE_STATUS_ERROR, "failed to write combination");
    }

    g_last_error = "ok";
    return MOOSE_STATUS_OK;
}

int moose_comb_free(moose_comb_handle comb) {
    CombHandle* ch = reinterpret_cast<CombHandle*>(comb);
    delete ch;
    return MOOSE_STATUS_OK;
}

int moose_db_get_object_json(moose_db_handle db, const char* name, char* out_json, size_t out_json_size) {
    DbHandle* h = reinterpret_cast<DbHandle*>(db);
    BRLCAD::ConstDatabase* cdb = as_const_db(h);
    if (!cdb) return fail(MOOSE_STATUS_INVALID_ARGUMENT, "db must not be NULL");
    if (!name || !out_json || out_json_size == 0) {
        return fail(MOOSE_STATUS_INVALID_ARGUMENT, "name/out_json/out_json_size invalid");
    }

    bool found = false;
    std::ostringstream ss;
    cdb->Get(name, [&](const BRLCAD::Object& obj) {
        found = true;
        ss << "{\"name\":\"" << json_escape(obj.Name()) << "\",";
        ss << "\"type\":\"" << json_escape(obj.Type()) << "\",";
        ss << "\"attributes\":{";
        bool first = true;
        BRLCAD::Object::AttributeIterator it = obj.FirstAttribute();
        while (it.Good()) {
            if (!first) ss << ",";
            first = false;
            ss << "\"" << json_escape(it.Key()) << "\":\"" << json_escape(it.Value()) << "\"";
            ++it;
        }
        ss << "}}";
    });

    if (!found) {
        return fail(MOOSE_STATUS_NOT_FOUND, "object not found");
    }

    std::string payload = ss.str();
    if (payload.size() + 1 > out_json_size) {
        return fail(MOOSE_STATUS_ERROR, "output buffer too small");
    }
    std::memcpy(out_json, payload.c_str(), payload.size() + 1);
    g_last_error = "ok";
    return MOOSE_STATUS_OK;
}

int moose_db_set_attribute(moose_db_handle db, const char* object_name, const char* key, const char* value) {
    DbHandle* h = reinterpret_cast<DbHandle*>(db);
    BRLCAD::Database* rw = as_rw_db(h);
    if (!rw) return fail(MOOSE_STATUS_NOT_WRITABLE, "database is not writable");
    if (!object_name || !key || !value) return fail(MOOSE_STATUS_INVALID_ARGUMENT, "object_name/key/value must not be NULL");

    bool updated = rw->Get(object_name, [&](BRLCAD::Object& obj) {
        obj.SetAttribute(key, value);
    });
    if (!updated) {
        return fail(MOOSE_STATUS_NOT_FOUND, "object not found or not writable");
    }
    g_last_error = "ok";
    return MOOSE_STATUS_OK;
}

int moose_db_get_attribute(moose_db_handle db, const char* object_name, const char* key, char* out_value, size_t out_value_size) {
    DbHandle* h = reinterpret_cast<DbHandle*>(db);
    BRLCAD::ConstDatabase* cdb = as_const_db(h);
    if (!cdb) return fail(MOOSE_STATUS_INVALID_ARGUMENT, "db must not be NULL");
    if (!object_name || !key || !out_value || out_value_size == 0) {
        return fail(MOOSE_STATUS_INVALID_ARGUMENT, "invalid get_attribute arguments");
    }

    bool found_obj = false;
    bool found_attr = false;
    std::string value;
    cdb->Get(object_name, [&](const BRLCAD::Object& obj) {
        found_obj = true;
        const char* attr = obj.Attribute(key);
        if (attr) {
            found_attr = true;
            value = attr;
        }
    });

    if (!found_obj) return fail(MOOSE_STATUS_NOT_FOUND, "object not found");
    if (!found_attr) return fail(MOOSE_STATUS_NOT_FOUND, "attribute not found");
    if (value.size() + 1 > out_value_size) return fail(MOOSE_STATUS_ERROR, "output buffer too small");

    std::memcpy(out_value, value.c_str(), value.size() + 1);
    g_last_error = "ok";
    return MOOSE_STATUS_OK;
}

const char* moose_last_error(void) {
    return g_last_error.c_str();
}
