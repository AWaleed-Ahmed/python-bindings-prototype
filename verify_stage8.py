from brlcad import Database
from brlcad.primitives.advanced_primitives import TGC, ELL
from brlcad.primitives.sphere import Sphere
from brlcad.combination import Combination
import os

def create_stage8_test_data(db_filename):
    """Creates the test database for verification."""
    if os.path.exists(db_filename):
        os.remove(db_filename)
        
    print(f"Creating test database: {db_filename}")
    with Database(db_filename, "w") as db:
        # Create Blades (TGC) with rotations
        # base=(0,0,0), height=(0,0,100), vectors A,B,C,D
        blade1 = TGC("blade1", [0,0,0], [0,0,100], [50,0,0], [0,10,0], [40,0,0], [0,8,0])
        blade1.create(db)
        
        blade2 = TGC("blade2", [0,0,0], [0,0,100], [50,0,0], [0,10,0], [40,0,0], [0,8,0]).rotate_z(120)
        blade2.create(db)
        
        blade3 = TGC("blade3", [0,0,0], [0,0,100], [50,0,0], [0,10,0], [40,0,0], [0,8,0]).rotate_z(240)
        blade3.create(db)
        
        # Create Hub (ELL)
        hub = ELL("hub", [0,0,50], [20,0,0], [0,20,0], [0,0,60])
        hub.create(db)
        
        # Create Combination (Propeller)
        db.create_combination("propeller", members=[blade1, blade2, blade3, hub])
        
        # Create Nested Combination
        ref_sph = Sphere("ref_sph", radius=10).translate(0, 0, 200)
        ref_sph.create(db)
        
        db.create_combination("assembly_nested", members=["propeller", ref_sph])

def verify_stage8(db_filename="test_advanced_stage8.g"):
    if not os.path.exists(db_filename):
        create_stage8_test_data(db_filename)
        
    print(f"\nOpening database for verification: {db_filename}")
    db = Database(db_filename, "r")
    
    print("\n1. Objects in database:")
    objs = db.list_objects()
    if not objs:
        print("  No objects found!")
    else:
        for obj in objs:
            print(f"  - {obj['name']} ({obj['type']})")

    # Note: get_combination and list_members are planned but might rely on raw list_objects for now
    # We will verify what we can via the existing API
    print("\n2. Hierarchy Verification (via list):")
    combs = [o for o in objs if o['type'] == 'comb']
    prims = [o for o in objs if o['type'] != 'comb']
    
    print(f"  Found {len(combs)} combinations and {len(prims)} primitives.")
    
    # Check for specific expected objects
    expected = ["blade1", "blade2", "blade3", "hub", "propeller", "assembly_nested"]
    found_names = [o['name'] for o in objs]
    for name in expected:
        status = "OK" if name in found_names else "MISSING"
        print(f"  - {name}: {status}")

    print("\n3. Advanced Primitives Check:")
    for pname in ["blade1", "hub"]:
        if pname in found_names:
            print(f"  - {pname} exists in database.")
        else:
            print(f"  - ERROR: {pname} not found.")

    db.close()
    print("\nStage 8 verification script finished.")

if __name__ == "__main__":
    verify_stage8()
