#this is my final API design that isn't implemented yet

from brlcad import Scene, Sphere, Mesh, union


# User-facing API: no raw matrix16, no manual face-index wiring unless user wants Mesh.
scene = Scene()

sph = Sphere("sph", radius=12.5).translate(0, 0, 0)

# Mesh helper hides low-level BOT details; user provides high-level geometry intent.
mesh = (
    Mesh.from_points(
        "mesh",
        points=[
            (0.0, 0.0, 0.0),
            (10.0, 0.0, 0.0),
            (0.0, 10.0, 0.0),
            (0.0, 0.0, 10.0),
        ],
        topology="tetra"   # helper decides faces internally
    )
    .translate(25, 0, 0)
    .rotate_z(15)
)

scene.add(sph)
scene.add(mesh)
scene.add(union("assembly", sph, mesh))

# Export path materializes transforms + member matrices internally.
scene.export("goal_scene.g")

# Unified read API remains simple.
with scene.open_database("goal_scene.g", mode="r") as db:
    print(db.read("assembly"))