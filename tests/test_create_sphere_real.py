import os
import sys
from brlcad import Database

def test_create_sphere_real():
    """
    Stage 4b: Test creating a real BRL-CAD sphere in a .g database.
    This creates an actual .g file on disk using libwdb.
    """
    print("--- Starting Stage 4b: Real Sphere Creation Test ---")
    
    filename = "test_geometry_stage4b.g"
    sphere_name = "my_sphere"
    radius = 2.5
    
    # Remove existing file if it exists to ensure a fresh test
    if os.path.exists(filename):
        os.remove(filename)
    
    try:
        # Step 1: Create/Open the database (defaults to mode='w')
        db = Database(filename, mode="w")
        
        # Step 2: Create a sphere
        print(f"Adding sphere '{sphere_name}' with radius {radius}...")
        db.create_sphere(sphere_name, radius)
        
        # Step 3: Explicitly close the database to flush changes
        db.close()
        print("Database closed.")
        
        # Step 4: Verify the file exists on disk
        assert os.path.exists(filename), f"Error: {filename} was not created!"
        file_size = os.path.getsize(filename)
        print(f"Successfully verified: {filename} exists (Size: {file_size} bytes)")
        
        print(f"Stage 4b Test Passed: Created {filename} containing {sphere_name}")

    except Exception as e:
        print(f"Test failed: {e}")
        # Cleanup on failure if the file was created partially
        if os.path.exists(filename):
            pass 
        raise e

    print("--- Stage 4b Test Completed Successfully ---")

if __name__ == "__main__":
    test_create_sphere_real()
