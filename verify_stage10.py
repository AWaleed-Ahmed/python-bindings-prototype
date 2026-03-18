import os
import subprocess
from brlcad.database import Database

DB_FILE = "stage12_test.g"
OUTPUT_PPM = "stage12_render.ppm"

def raytrace_scene():
    """
    Raytraces the stage12_test.g database created in the previous stage.
    """
    if not os.path.exists(DB_FILE):
        print(f"[ERROR] Database file {DB_FILE} not found. Please run verify_stage12.py first.")
        return

    print(f"\n--- Raytracing {DB_FILE} ---")

    # We'll use the 'rt' command from BRL-CAD to render the scene.
    # 'comb_1' is the name of the exported scene from BRL-CADExporter.
    command = [
        "rt",
        "-o", OUTPUT_PPM,       # Output file
        "-w", "1024",           # Width
        "-n", "1024",           # Height
        "-V", "1:1",            # Aspect ratio
        "-P", "1",              # Number of processors (1 for predictability)
        DB_FILE,                # The database file
        "comb_1"                # The object to render
    ]

    print(f"Running command: {' '.join(command)}")
    
    try:
        # Run the raytracer. We'll provide standard 'view' inputs via stdin to center the object.
        # This setup (eye/center) should capture the spheres around the origin.
        render_script = "viewsize 15; eye 10 10 10; center 0 0 0; start 0; clean;"
        
        result = subprocess.run(
            command,
            input=render_script,
            text=True,
            capture_output=True
        )

        if result.returncode == 0:
            print(f"[SUCCESS] Rendered scene to {OUTPUT_PPM}")
            if os.path.exists(OUTPUT_PPM):
                print(f"File size: {os.path.getsize(OUTPUT_PPM)} bytes")
        else:
            print(f"[ERROR] Raytracing failed with exit code {result.returncode}")
            print(f"Stderr: {result.stderr}")

    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")

if __name__ == "__main__":
    raytrace_scene()
