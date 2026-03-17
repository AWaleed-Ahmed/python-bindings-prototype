import os
import sys
from brlcad import Database

def test_read_sphere():
    """
    Stage 5: Test reading objects and sphere attributes from an existing .g file.
    """
    print("--- Starting Stage 5: Database Read Test ---")
    
    # Use the database created in Stage 4b
    filename = "test_geometry_stage4b.g"
    
    if not os.path.exists(filename):
        print(f"Error: {filename} not found. Please run Stage 4b test first.")
        return

    try:
        # Step 1: Open database in read-only mode
        db = Database(filename, mode="r")
        print(f"Opened {filename} for reading.")

        # Step 2: List all objects
        objects = db.list_objects()
        print(f"Objects in database: {objects}")
        
        # Verify 'my_sphere' is present
        names = [obj['name'] for obj in objects]
        assert "my_sphere" in names, "my_sphere not found in database!"

        # Step 3: Get specific sphere attributes
        sphere = db.get_sphere("my_sphere")
        print(f"Retrieved sphere: {sphere.name}, radius: {sphere.radius}, center: {sphere.origin}")
        
        # Step 4: Verify attributes
        assert sphere.radius == 2.5, f"Expected radius 2.5, got {sphere.radius}"
        assert sphere.origin == [0.0, 0.0, 0.0], f"Expected center [0, 0, 0], got {sphere.origin}"

        print("Stage 5 Test Passed: Successfully listed objects and read sphere attributes.")
        db.close()

    except Exception as e:
        print(f"Test failed: {e}")
        raise e

    print("--- Stage 5 Test Completed Successfully ---")

if __name__ == "__main__":
    test_read_sphere()
