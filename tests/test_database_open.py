import os
import sys
from brlcad import Database

# Helper to find the _brlcad extension
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

def test_database_open():
    """
    Test Stage 3: Opening a BRL-CAD .g database through the high-level 
    Python API and verifying the internal PyCapsule creation.
    """
    print("--- Starting Stage 3: Database Open Test ---")
    
    filename = "test_geometry.g"
    mode = "w"
    
    try:
        # Step 1: Initialize the high-level Database object
        # This calls: Python Database -> C py_brlcad_db_open -> C adapter brlcad_db_open
        db = Database(filename, mode=mode)
        
        # Step 2: Verify the filename is stored correctly
        assert db.filename == filename
        
        # Step 3: Verify that a PyCapsule was successfully created and stored
        assert db._db_capsule is not None
        print(f"Database object created. Filename: {db.filename}")
        print(f"Internal capsule stored: {db._db_capsule}")
        
        # Step 4: Verify the capsule name if possible (manual check in debug output)
        print("Successfully opened database and stored native pointer in capsule.")

        # Step 5: Close the database (triggers destructor hook)
        db.close()
        assert db._db_capsule is None
        print("Database closed and capsule cleared.")

    except Exception as e:
        print(f"Test failed: {e}")
        # Re-raise to trigger exit code 1 if needed
        raise e

    print("--- Stage 3 Test Completed Successfully ---")

if __name__ == "__main__":
    test_database_open()
