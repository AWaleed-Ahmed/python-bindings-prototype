"""
Example script to create a sphere in a BRL-CAD .g file.
"""
from brlcad import Database, Sphere

def main():
    # Database uses context manager for safe cleanup
    with Database("example.g", "Test Database") as db:
        # High-level Pythonic API
        s1 = Sphere(name="sphere.s", origin=(0, 0, 0), radius=10.0)
        s1.create(db)
        
        print(f"Sphere {s1.name} created successfully in {db.filename}.")

if __name__ == "__main__":
    main()
