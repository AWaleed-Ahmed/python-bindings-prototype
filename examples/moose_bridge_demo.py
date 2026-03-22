"""Demo for native MOOSE-first modeling via BRLCADExporter.export_moose()."""
from brlcad.database import Database
from brlcad.exporter import BRLCADExporter
from brlcad.moose import MooseSphere, MooseBox, MooseCylinder


def main():
    db_file = "moose_bridge_demo.g"
    exporter = BRLCADExporter(filename=db_file)

    s1 = MooseSphere(10).translate(25, 0, 0)
    s2 = MooseSphere(4).translate(-8, 0, 0)
    b1 = MooseBox(8, 5, 4).translate(0, 10, 0)
    c1 = MooseCylinder(2, 12).translate(0, 0, -6)

    # Default path: combination member-matrix transforms.
    base_union = s1 + s2

    # Optional path: explicit primitive transform mode on one object.
    s2.primitive_transforms()

    scene = (base_union + b1) - c1

    with Database(db_file, "w") as db:
        name = exporter.export_moose(scene, db=db)
        print(f"Exported MOOSE-style scene as: {name}")
        print(f"Objects: {db.list_objects()}")


if __name__ == "__main__":
    main()
