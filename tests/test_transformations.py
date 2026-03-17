import os
import sys

# Ensure project source is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from brlcad.database import Database

def test_transformations():
    print("--- Starting Stage 7: Transformations Test ---")
    db_file = "test_transform_stage7.g"
    if os.path.exists(db_file):
        os.remove(db_file)

    try:
        with Database(db_file, "w") as db:
            print("[test] Creating sphere s1...")
            s1 = db.create_sphere("s1", radius=10.0)
            
            print("[test] Applying transformations to s1 (translate [100, 0, 0], rotate_z 45, scale 0.5)...")
            s1.translate(100, 0, 0).rotate_z(45).scale(0.5)
            
            print("[test] Creating assembly1 with transformed s1...")
            assembly = db.create_combination("assembly1", members=[s1])
            
            print("[test] Creating s2...")
            s2 = db.create_sphere("s2", radius=5.0)
            
            print("[test] Creating top_level assembly with assembly1 and s2 (translated [0, 50, 0])...")
            # We'll transform assembly itself
            assembly.translate(0, 50, 0)
            
            top = db.create_combination("top_level", members=[assembly, s2])
            
        print("[test] Database closed. Re-opening for verification with MGED...")
        
        # Verify using MGED to list members and their transformations
        import subprocess
        # Use mged 'list' command on assembly1 and top_level
        # -c for command mode
        print("\n--- MGED list assembly1 ---")
        subprocess.run(["mged", "-c", db_file, "list", "assembly1"])
        
        print("\n--- MGED list top_level ---")
        subprocess.run(["mged", "-c", db_file, "list", "top_level"])
        
        print("\nStage 7 Test (Visual/Manual Check): Verify matrices in MGED output.")
        print("s1 should have a 4x4 matrix in 'assembly1'")
        print("assembly1 should have a 4x4 matrix in 'top_level'")

    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_transformations()
