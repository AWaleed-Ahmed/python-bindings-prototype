"""
Unit tests for the Database class.
"""
import unittest
from brlcad import Database

class TestDatabase(unittest.TestCase):
    def test_database_init(self):
        """Test database initialization and structure."""
        db = Database("test.g", "Test DB")
        self.assertEqual(db.filename, "test.g")
        
    def test_database_context(self):
        """Test database context manager behavior."""
        with Database("context_test.g", "Title") as db:
            self.assertIsNotNone(db._db_capsule)
        
        # db_capsule should be cleaned up after exit
        self.assertIsNone(db._db_capsule)

if __name__ == "__main__":
    unittest.main()
