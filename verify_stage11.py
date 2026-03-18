import unittest
from brlcad import Sphere, Box, Cylinder, CSGNode

class TestHighLevelAPI(unittest.TestCase):

    def test_sphere_creation(self):
        s = Sphere(5)
        self.assertEqual(s.radius, 5)

    def test_box_creation(self):
        b = Box(1, 2, 3)
        self.assertEqual((b.x, b.y, b.z), (1, 2, 3))

    def test_cylinder_creation(self):
        c = Cylinder(2, 10)
        self.assertEqual((c.r, c.h), (2, 10))

    def test_translate_chain(self):
        s = Sphere(2)
        s2 = s.translate(1, 2, 3)

        self.assertNotEqual(id(s), id(s2))  # should return new object
        self.assertEqual(s2.transforms[-1], ("translate", (1, 2, 3)))

    def test_color_assignment(self):
        s = Sphere(2).color(255, 0, 0)
        self.assertEqual(s.color_value, (255, 0, 0))

    def test_shader_assignment(self):
        s = Sphere(2).shader("plastic")
        self.assertEqual(s.shader_name, "plastic")

    def test_union_operation(self):
        s1 = Sphere(2)
        s2 = Sphere(1)

        scene = s1 + s2

        self.assertIsInstance(scene, CSGNode)
        self.assertEqual(scene.operation, "union")
        self.assertEqual(scene.left, s1)
        self.assertEqual(scene.right, s2)

    def test_subtraction_operation(self):
        s1 = Sphere(2)
        s2 = Sphere(1)

        scene = s1 - s2

        self.assertEqual(scene.operation, "subtract")

    def test_intersection_operation(self):
        s1 = Sphere(2)
        s2 = Sphere(1)

        scene = s1 & s2

        self.assertEqual(scene.operation, "intersect")

    def test_complex_composition(self):
        s1 = Sphere(2).translate(0, 0, 5)
        s2 = Sphere(1).translate(3, 0, 0)

        scene = (s1 + s2).color(0, 255, 0)

        self.assertIsInstance(scene, CSGNode)
        self.assertEqual(scene.color_value, (0, 255, 0))
    

if __name__ == "__main__":
    unittest.main()
