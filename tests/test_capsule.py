import _brlcad

def test_capsule():
    """
    Tests the C extension infrastructure for PyCapsule pointer storage.
    Ensures that native pointers can be successfully wrapped and retrieved.
    """
    value = _brlcad.test_capsule()
    assert value == 42
    print("PyCapsule infrastructure test passed! Value: %d" % value)

if __name__ == "__main__":
    test_capsule()
