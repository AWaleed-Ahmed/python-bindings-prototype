import os
import subprocess
from brlcad import Sphere, BRLCADExporter
from brlcad.database import Database

def check(label, actual, expected):
    if actual == expected:
        print(f"[PASS] {label}: {actual}")
    else:
        print(f"[FAIL] {label}: got {actual}, expected {expected}")

class BRLCADRaytracer:
    """
    Handles raytracing of BRL-CAD .g files using the 'rt' command.
    """
    def __init__(self, db_file):
        self.db_file = db_file
        if not os.path.exists(db_file):
            raise FileNotFoundError(f"Database file {db_file} not found.")

    def render(self, object_name, output_ppm, width=512, height=512, view_params=None):
        """
        Executes the 'rt' command to render a specific object.
        """
        print(f"\n--- Rendering {object_name} from {self.db_file} ---")
        
        # Build the rt command
        # -o: output file
        # -s: square resolution (width)
        # -w: width
        # -n: height
        # -V: aspect ratio
        command = [
            "rt",
            "-o", output_ppm,
            "-w", str(width),
            "-n", str(height),
            "-V", f"{width}:{height}",
            self.db_file,
            object_name
        ]

        # Default view parameters if none provided
        if view_params is None:
            view_params = "viewsize 10; eye 10 10 10; center 0 0 0; start 0; clean;"

        print(f"Executing: {' '.join(command)}")
        try:
            result = subprocess.run(
                command,
                input=view_params,
                text=True,
                capture_output=True
            )
            if result.returncode == 0:
                print(f"[SUCCESS] Raytrace completed: {output_ppm}")
                return True
            else:
                print(f"[ERROR] Raytrace failed (code {result.returncode})")
                print(f"Stderr: {result.stderr}")
                return False
        except Exception as e:
            print(f"[ERROR] Exception during raytrace: {e}")
            return False

    def convert_to_png(self, ppm_file, png_file):
        """
        Converts PPM to PNG using ImageMagick 'convert'.
        """
        try:
            subprocess.run(["convert", ppm_file, png_file], check=True)
            print(f"[SUCCESS] Converted to {png_file}")
            return True
        except Exception as e:
            print(f"[WARNING] Conversion to PNG failed: {e}")
            return False

def verify_stage13():
    db_file = "stage13_scene.g"
    ppm_file = "stage13_render.ppm"
    png_file = "stage13_render.png"

    if os.path.exists(db_file):
        os.remove(db_file)

    print("--- Stage 13: Raytracing & Verification ---")

    # 1. Create a scene using Stage 11/12 API
    # Two spheres unioned, colored green
    s1 = Sphere(2).translate(-1, 0, 0).color(0, 255, 0).shader("plastic")
    s2 = Sphere(2).translate(1, 0, 0).color(0, 255, 0).shader("plastic")
    scene = s1 + s2

    # 2. Export using Stage 12 Exporter
    exporter = BRLCADExporter(db_file)
    root_name = exporter.export(scene)
    print(f"Exported scene root: {root_name}")

    # 3. Verify Database Attributes
    with Database(db_file, "r") as db:
        objs = db.list_objects()
        check("Root object exists", root_name in objs, True)
        
        # Check colors and shaders for internal primitives (sph_1, sph_2)
        # Note: In our exporter, names are sph_1, sph_2...
        check("sph_1 color", db.get_color("sph_1"), (0, 255, 0))
        check("sph_1 shader", db.get_shader("sph_1"), "plastic")
        check("sph_2 color", db.get_color("sph_2"), (0, 255, 0))

    # 4. Raytrace the scene
    raytracer = BRLCADRaytracer(db_file)
    # Camera view: looking at origin from (10, 10, 10)
    view = "viewsize 12; eye 8 8 8; center 0 0 0; start 0; clean;"
    if raytracer.render(root_name, ppm_file, width=800, height=800, view_params=view):
        # 5. Optional Image Conversion
        raytracer.convert_to_png(ppm_file, png_file)

    print("\n--- Stage 13 Verification Complete ---")

if __name__ == "__main__":
    verify_stage13()
