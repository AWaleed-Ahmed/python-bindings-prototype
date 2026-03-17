import sys
import os
from brlcad.database import Database

def test_attributes():
    db_file = "test_attributes.g"
    if os.path.exists(db_file):
        os.remove(db_file)

    print(f"--- Testing attributes in {db_file} ---")
    
    with Database(db_file, "w") as db:
        # 1. Create primitives
        s1 = db.create_sphere("s1", 2.5)
        s1.set_region(10)
        s1.set_shader("metallic")

        s2 = db.create_sphere("s2", 5.0)
        s2.set_region(15)
        s2.set_shader("plastic")

        # 2. Create combination
        comb = db.create_combination("assembly1", members=[s1, s2])
        comb.set_region(20)
        comb.set_shader("matte")

        # 3. Retrieve and assert
        print(f"Checking {s1.name}:")
        r1 = s1.get_region()
        sh1 = s1.get_shader()
        print(f"  Region: {r1} (expected 10)")
        print(f"  Shader: '{sh1}' (expected 'metallic')")
        
        assert r1 == 10
        assert sh1 == "metallic"

        print(f"Checking {s2.name}:")
        r2 = s2.get_region()
        sh2 = s2.get_shader()
        print(f"  Region: {r2} (expected 15)")
        print(f"  Shader: '{sh2}' (expected 'plastic')")
        
        assert r2 == 15
        assert sh2 == "plastic"

        print(f"Checking {comb.name}:")
        rc = comb.get_region()
        shc = comb.get_shader()
        print(f"  Region: {rc} (expected 20)")
        print(f"  Shader: '{shc}' (expected 'matte')")
        
        assert rc == 20
        assert shc == "matte"

        print("--- Attribute tests PASSED ---")

if __name__ == "__main__":
    # Ensure src is in PYTHONPATH
    sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
    
    try:
        test_attributes()
    except Exception as e:
        print(f"Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
