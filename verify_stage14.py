import os
import subprocess
from brlcad import Sphere, BRLCADExporter
from brlcad.database import Database

def check(label, actual, expected):
    if actual == expected:
        print(f"[PASS] {label}: {actual}")
    else:
        print(f"[FAIL] {label}: got {actual}, expected {expected}")

def raytrace(db_file, obj_name, out_file):
    print(f"--- Raytracing {obj_name} to {out_file} ---")
    cmd = ["rt", "-o", out_file, "-w", "512", "-n", "512", db_file, obj_name]
    view = "viewsize 10; eye 10 10 10; center 0 0 0; start 0; clean;"
    subprocess.run(cmd, input=view, text=True, capture_output=True)

def verify_stage14():
    db_file = "stage14_dynamic.g"
    if os.path.exists(db_file):
        os.remove(db_file)

    print("--- Stage 14: Dynamic Manipulation & Attribute Updates ---")

    # 1. Initial Scene Setup
    s1 = Sphere(2).color(255, 0, 0).shader("plastic") # Red
    s2 = Sphere(1.5).translate(2, 0, 0).color(0, 0, 255) # Blue
    scene = s1 + s2
    
    exporter = BRLCADExporter(db_file)
    root_name = exporter.export(scene)
    
    print(f"Initial export done. Root: {root_name}")
    raytrace(db_file, root_name, "stage14_initial.ppm")

    # 2. Dynamic Attribute Updates at Runtime (Object Selection/Manipulation)
    # We use the existing scene object (or we could recreate it pointing to same names)
    print("\nUpdating attributes in memory and re-exporting...")
    
    # Update color of s1 to Yellow in-place or via selection
    s1.set_color(255, 255, 0).set_shader("metallic") 
    
    # Update color of s2 to Magenta
    s2.set_color(255, 0, 255)

    # 3. Scene Update (Re-render)
    # Re-exporting should update the DB objects without recreating primitives
    exporter.export(scene)
    
    print("Re-export (update) done.")
    raytrace(db_file, root_name, "stage14_updated.ppm")

    # 4. Verification
    with Database(db_file, "r") as db:
        print("\nVerifying updated attributes in BRL-CAD database:")
        check("s1 updated color", db.get_color("sph_1"), (255, 255, 0))
        check("s1 updated shader", db.get_shader("sph_1"), "metallic")
        check("s2 updated color", db.get_color("sph_2"), (255, 0, 255))

    # Optional: Convert to PNG for viewing
    subprocess.run(["convert", "stage14_updated.ppm", "stage14_updated.png"])
    print("\n--- Stage 14 Verification Complete ---")

if __name__ == "__main__":
    verify_stage13_file = "stage13_scene.g" # Check if user wanted to load this
    verify_stage14()
