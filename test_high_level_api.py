from src.brlcad.high_level_api import Sphere, Box, Cylinder

def test_api():
    # s1 = Sphere(2).translate(0, 0, 5)
    s1 = Sphere(2).translate(0, 0, 5)
    print(f"Created Sphere(2) with transformations: {s1._transformations}")

    # s2 = Sphere(1).translate(3, 0, 0)
    s2 = Sphere(1).translate(3, 0, 0)
    print(f"Created Sphere(1) with transformations: {s2._transformations}")

    # scene = (s1 + s2).color(0, 255, 0)
    scene = (s1 + s2).color(0, 255, 0)
    print(f"Created scene with op: {scene.op_type}")
    print(f"Scene color: {scene._color}")

    # Complex example
    b = Box(1, 1, 1).rotate(45, 0, 0)
    c = Cylinder(0.5, 2)
    complex_scene = (s1 - b) & c
    print(f"Complex scene op: {complex_scene.op_type}")
    print(f"Left: {complex_scene.left.op_type} ({complex_scene.left.left.__class__.__name__} - {complex_scene.left.right.__class__.__name__})")
    print(f"Right: {complex_scene.right.__class__.__name__}")

if __name__ == "__main__":
    test_api()
