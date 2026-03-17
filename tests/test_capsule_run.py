import _brlcad
import gc

def run_capsule_test():
    """
    Test script to verify the Stage 2 PyCapsule infrastructure.
    Calls the test_capsule() function in the C extension.
    """
    print("--- Starting Stage 2 PyCapsule Test ---")

    # Step 1: Call the C function
    # It allocates memory for an integer (42), wraps it in a capsule,
    # retrieves the pointer, copies the value, frees the memory,
    # and returns the value to Python.
    try:
        value = _brlcad.test_capsule()
        print(f"Received value from C extension: {value}")
        
        # Step 2: Verify the value is correctly returned
        assert value == 42, "PyCapsule infrastructure failed! Expected 42."
        print(f"Stage 2 PyCapsule test passed: {value}")

    except Exception as e:
        print(f"Test failed with error: {e}")
        return

    # Step 3: Trigger Python Garbage Collection
    # Since test_capsule() in C already calls Py_DECREF on the capsule,
    # the destructor should have already executed.
    # We call collect() to ensure any remaining references are cleaned up.
    print("Triggering garbage collection to verify destructor activity...")
    gc.collect()

    print("--- Test Completed ---")

if __name__ == "__main__":
    run_capsule_test()
