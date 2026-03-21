# test_stage12.py
import os
from brlcad import Sphere, Box
from brlcad import BRLCADExporter
from brlcad.database import Database

def check(label, actual, expected):
    if actual == expected:
        print(f"[PASS] {label}: {actual}")
    else:
        print(f"[FAIL] {label}: got {actual}, expected {expected}")

def verify_stage12():
    db_file = "stage12_test.g"
    if os.path.exists(db_file):
        os.remove(db_file)

    print(f"\n--- Stage 12 Verification: Exporting scene to {db_file} ---")

    # Create a high-level scene
    s1 = Sphere(2).translate(0, 0, 5).color(255, 0, 0).shader("metallic")
    s2 = Sphere(1).translate(3, 0, 0).color(0, 255, 0).shader("plastic")
    scene = s1 + s2  # Union of two spheres

    # Export scene to BRL-CAD
    exporter = BRLCADExporter(db_file)
    exporter.export(scene)

    # Open database and verify objects
    with Database(db_file, "r") as db:
        objs = db.list_objects()
        check("Database file created", os.path.exists(db_file), True)
        check("Sphere s1 exists", "sph_1" in objs, True)
        check("Sphere s2 exists", "sph_2" in objs, True)
        check("Combination exists", "comb_1" in objs, True)

        # Check colors (should be RGB tuples)
        s1_color = db.get_color("sph_1")
        s2_color = db.get_color("sph_2")
        comb_color = db.get_color("comb_1")

        check("sph_1 color", s1_color, (255, 0, 0))
        check("sph_2 color", s2_color, (0, 255, 0))
        check("comb_1 color", comb_color, None)  # combination inherits None if not set

        # Check shaders
        check("sph_1 shader", db.get_shader("sph_1"), "metallic")
        check("sph_2 shader", db.get_shader("sph_2"), "plastic")
        check("comb_1 shader", db.get_shader("comb_1"), None)

    print("\n--- Stage 12 Verification Complete ---")

if __name__ == "__main__":
    verify_stage12()
    
    
    
    
    
from brlcad import Sphere

# Create two spheres with transformations, color, and shader
s1 = Sphere(2).translate(0, 0, 5).color(255, 0, 0).shader("metallic")
s2 = Sphere(1).translate(3, 0, 0).color(0, 255, 0).shader("plastic")

# Combine spheres (CSG Union) and demonstrate in-place updates
s1.set_color(255, 255, 0).set_shader("metallic")
s2.set_color(255, 0, 255)
scene = s1 + s2