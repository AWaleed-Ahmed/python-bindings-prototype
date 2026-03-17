# from brlcad.database import Database

# # Open Stage 6 database
# db = Database("test_combinations_stage6.g", "r")

# # List all objects in the database
# print("Objects in database:")
# for obj in db.list_objects():
#     print(obj)

# # List all combinations by filtering objects
# print("\nCombinations and members:")
# for obj in db.list_objects():
#     if obj['type'] == 'primitive':  # all combinations are currently marked 'primitive'
#         name = obj['name']
#         try:
#             comb_members = db.list_combination_members(name)
#             print(f"{name} members: {comb_members}")
#         except AttributeError:
#             # If list_combination_members doesn't exist, skip
#             pass

# db.close()

# from brlcad.database import Database

# db = Database("test_transform_stage7.g", "r")
# print("Objects in database:")
# for obj in db.list_objects():
#     print(obj)
# db.close()

import os
from brlcad.database import Database
from brlcad.advanced_primitives import TGC, ELL

# Stage 8 Test: Advanced Primitives
db_filename = "test_advanced_stage8.g"

# Remove existing test DB if it exists
if os.path.exists(db_filename):
    os.remove(db_filename)

# Create a new BRL-CAD database
db = Database(db_filename, "w")

# Create advanced primitives
tgc1 = db.create_tgc(
    name="blade1",
    base=[0, 0, 0],
    apex=[1, 0, 0],
    top=[1, 1, 0],
    bottom=[0, 1, 0]
).rotate_z(0)  # initial orientation

tgc2 = db.create_tgc(
    name="blade2",
    base=[0, 0, 0],
    apex=[1, 0, 0],
    top=[1, 1, 0],
    bottom=[0, 1, 0]
).rotate_z(120)  # rotated 120 degrees

tgc3 = db.create_tgc(
    name="blade3",
    base=[0, 0, 0],
    apex=[1, 0, 0],
    top=[1, 1, 0],
    bottom=[0, 1, 0]
).rotate_z(240)  # rotated 240 degrees

ell_hub = db.create_ell(
    name="hub",
    radii=[0.5, 0.5, 0.5]
)

# Create a combination for the propeller
propeller = db.create_combination("propeller")
propeller.add_primitive(tgc1)
propeller.add_primitive(tgc2)
propeller.add_primitive(tgc3)
propeller.add_primitive(ell_hub)

# Commit and close the database
db.close()

# Re-open database for verification
db = Database(db_filename, "r")
print("Objects in database:")
for obj in db.list_objects():
    print(obj)

# Verify propeller members
prop = db.get_combination("propeller")
members = prop.list_members()
print("\nMembers of 'propeller':")
for m in members:
    print(m)

db.close()