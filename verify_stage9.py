"""
Stage 9 Verification: Attribute Management

This test checks:
1. Setting and getting region + shader
2. Default values (no attributes set)
3. Overwriting attributes
4. Multiple primitives
5. Combination attributes
6. Stability (no crashes)
"""

from brlcad.database import Database

def check(label, actual, expected):
    if actual == expected:
        print(f"[PASS] {label}: {actual}")
    else:
        print(f"[FAIL] {label}: got {actual}, expected {expected}")

def verify_stage9():
    db_name = "test_stage9_full.g"
    print(f"\n--- Running Stage 9 Tests on {db_name} ---")

    db = Database(db_name, "w")

    # =========================
    # 1. BASIC ATTRIBUTE TEST
    # =========================
    s1 = db.create_sphere("s1", 2.0)
    s1.set_region(10)
    s1.set_shader("metallic")

    check("s1 region", s1.get_region(), 10)
    check("s1 shader", s1.get_shader(), "metallic")

    # =========================
    # 2. DEFAULT VALUES TEST
    # =========================
    s2 = db.create_sphere("s2", 3.0)

    try:
        region = s2.get_region()
        shader = s2.get_shader()
        print(f"[INFO] s2 default region: {region}")
        print(f"[INFO] s2 default shader: {shader}")
    except Exception as e:
        print("[FAIL] Default attribute access crashed:", e)

    # =========================
    # 3. OVERWRITE TEST
    # =========================
    s1.set_region(99)
    s1.set_shader("plastic")

    check("s1 overwrite region", s1.get_region(), 99)
    check("s1 overwrite shader", s1.get_shader(), "plastic")

    # =========================
    # 4. MULTIPLE OBJECTS TEST
    # =========================
    s3 = db.create_sphere("s3", 1.0)
    s4 = db.create_sphere("s4", 4.0)

    s3.set_region(30)
    s4.set_region(40)

    check("s3 region", s3.get_region(), 30)
    check("s4 region", s4.get_region(), 40)

    # =========================
    # 5. COMBINATION TEST
    # =========================
    comb = db.create_combination("assembly1", members=[s1, s2])

    comb.set_region(200)
    comb.set_shader("matte")

    check("comb region", comb.get_region(), 200)
    check("comb shader", comb.get_shader(), "matte")

    # =========================
    # 6. ISOLATION TEST
    # =========================
    # Ensure attributes don't leak between objects
    check("s1 still region 99", s1.get_region(), 99)
    check("s2 still unchanged", s2.get_region(), None)
    
    # Test Raw access
    check("s2 raw region", s2.get_region_raw(), 0)

    db.close()

    print("\n--- Stage 9 Testing Complete ---")

if __name__ == "__main__":
    verify_stage9()