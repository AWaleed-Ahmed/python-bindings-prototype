from brlcad import Database, Sphere, BRLCADExporter
import os

def test_exporter():
    db_file = "scene.g"
    if os.path.exists(db_file):
        os.remove(db_file)
    
    # Define scene using High-Level API
    s1 = Sphere(2)
    s2 = Sphere(1).translate(3, 0, 0)
    
    # Union of two spheres with color
    scene = (s1 + s2).color(0, 255, 0)
    
    # Export to BRL-CAD
    exporter = BRLCADExporter()
    with Database(db_file) as db:
        name = exporter.export(scene, db)
        print(f"Exported scene as: {name}")
        
        # Verify objects in database
        objects = db.list_objects()
        print(f"Objects in database: {[o['name'] for o in objects]}")

if __name__ == "__main__":
    test_exporter()
