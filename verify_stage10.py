# from brlcad.database import Database
# import os

# def check(label, actual, expected):
#     if actual == expected:
#         print(f"[PASS] {label}: {actual}")
#     else:
#         print(f"[FAIL] {label}: got {actual}, expected {expected}")

# def verify_stage10():
#     db_name = "test_stage10.g"
#     if os.path.exists(db_name):
#         os.remove(db_name)
    
#     print(f"\n--- Running Stage 10 Tests on {db_name} ---")

#     with Database(db_name, "w") as db:
#         s = db.create_sphere("s1", 2.0)

#         # Test Fluent API and all new attributes
#         s.set_region(True)\
#          .set_region_id(100)\
#          .set_los(50)\
#          .set_material_id(7)\
#          .set_color(255, 0, 0)\
#          .set_shader("plastic")

#         print("Verifying s1 attributes:")
#         check("region flag", s.is_region(), True)
#         check("region ID", s.get_region(), 100)
#         check("LOS", s.get_los(), 50)
#         check("material ID", s.get_material_id(), 7)
#         check("color", s.get_color(), (255, 0, 0))
#         check("shader", s.get_shader(), "plastic")

#         # Test defaults
#         s2 = db.create_sphere("s2", 1.0)
#         print("\nVerifying s2 defaults:")
#         check("s2 default region flag", s2.is_region(), False)
#         check("s2 default color", s2.get_color(), None)

#         # Test combination attributes
#         comb = db.create_combination("comb1", members=[s, s2])
#         comb.set_region(True).set_region_id(200).set_color(0, 255, 0)
        
#         print("\nVerifying comb1 attributes:")
#         check("comb1 region flag", comb.is_region(), True)
#         check("comb1 region ID", comb.get_region(), 200)
#         check("comb1 color", comb.get_color(), (0, 255, 0))

#     print("\n--- Stage 10 Testing Complete ---")

# if __name__ == "__main__":
#     verify_stage10()


import os
import subprocess
from brlcad.database import Database
from brlcad.primitives.primitive import Transformable

DB_FILE = "stage12_test.g"
OUTPUT_PPM = "output1.ppm"
OUTPUT_PNG = "output2.png"
VIEW_FILE = "render_view.v"

# Helper for colored output check
def check(label, actual, expected):
    print(f"[INFO] {label}: {actual} (expected {expected})")

def prepare_database():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

    with Database(DB_FILE, "w") as db:
        # Create primitives with shaders/colors
        s1 = db.create_sphere("s1", 2.0)
        s1.set_shader("metallic").set_color(255, 0, 0)

        s2 = db.create_sphere("s2", 1.5)
        s2.set_shader("plastic").set_color(0, 0, 255)

        # Create combination
        comb = db.create_combination("comb1", members=[s1, s2])
        comb.set_shader("matte").set_color(0, 255, 0)

        # Verify
        check("s1 shader", s1.get_shader(), "metallic")
        check("s2 shader", s2.get_shader(), "plastic")
        check("comb1 shader", comb.get_shader(), "matte")

VIEW_FILE = "render_view.v"

def save_camera_view():
    # BRL-CAD 'rt' -M mode expects a setup script containing MGED-like view commands.
    view_content = """\
viewsize 10.0;
orientation 0.248097 0.476591 0.748097 0.389435;
eye_pt 10 10 10;
start 0; clean;
end;
"""
    with open(VIEW_FILE, "w") as f:
        f.write(view_content)
    print(f"[INFO] Camera view saved to {VIEW_FILE}")

def run_raytracer():
    if os.path.exists(OUTPUT_PPM):
        os.remove(OUTPUT_PPM)

    # Simplified command without -M and -V for basic azimuth/elevation rendering
    # or use them if view_content is correctly formatted as above.
    cmd = [
        "rt",
        "-a", "35", "-e", "25", # Azimuth/Elevation
        "-s", "512",            # resolution
        "-o", OUTPUT_PPM,
        DB_FILE,
        "comb1"                 # render only this combination
    ]
    print(f"[INFO] Running raytracer: {' '.join(cmd)}")
    # We provide empty input to stdin so 'rt' doesn't wait for interactive input
    subprocess.run(cmd, input=b'', check=True)

    # Convert PPM to PNG
    if os.path.exists(OUTPUT_PPM):
        subprocess.run(["convert", OUTPUT_PPM, OUTPUT_PNG], check=True)
        print(f"[INFO] Output saved as {OUTPUT_PNG}")
    else:
        print("[ERROR] Raytracer did not produce output.ppm")

if __name__ == "__main__":
    prepare_database()
    save_camera_view()
    run_raytracer()