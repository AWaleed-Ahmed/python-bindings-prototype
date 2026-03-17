import os
import sys

# Ensure project source is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from brlcad.database import Database

def test_combinations():
    print("--- Starting Stage 6: Combinations Test ---")
    db_file = "test_combinations_stage6.g"
    if os.path.exists(db_file):
        os.remove(db_file)

    try:
        with Database(db_file, "w") as db:
            # 1. Create primitives
            print("[test] Creating primitives...")
            db.create_sphere("s1", radius=2.5)
            db.create_sphere("s2", radius=1.0)
            
            # 2. Create combination
            print("[test] Creating combination 'assembly1'...")
            # We'll simulate passing names directly or objects if they had names
            class Primitive:
                def __init__(self, name): self.name = name
                
            s1 = Primitive("s1")
            s2 = Primitive("s2")
            
            # In real system, Database.create_sphere would return a Primitive object,
            # but currently it returns None. We'll fix that later.
            
            comb = db.create_combination("assembly1", members=[s1, s2])
            print(f"[test] Combo created: {comb}")
            
            # 3. Create nested combination
            print("[test] Creating nested combination 'recursive'...")
            nested = db.create_combination("recursive", members=[Primitive("assembly1"), Primitive("s1")])
            
        print("[test] Database closed. Re-opening for verification...")
        
        # 4. Verify contents
        with Database(db_file, "r") as db:
            objects = db.list_objects()
            print(f"Objects in database: {objects}")
            
            names = [obj['name'] for obj in objects]
            assert "s1" in names
            assert "s2" in names
            assert "assembly1" in names
            assert "recursive" in names
            
            print("Stage 6 Test Passed: Successfully created primitives and combinations.")

    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_combinations()
