from brlcad import Database
from brlcad.primitives.sphere import Sphere
from brlcad.primitives.advanced_primitives import TGC, ELL
from brlcad.combination import Combination

def test_advanced_primitives():
    with Database("advanced.g", mode="w") as db:
        # Create a TGC (Cone/Cylinder)
        # base=(0,0,0), height=(0,0,50), vectors=(20,0,0), (0,20,0), (10,0,0), (0,10,0)
        # This describes a truncated cone
        tgc = TGC("my_cone", 
                  [0, 0, 0], [0, 0, 50], 
                  [20, 0, 0], [0, 20, 0], 
                  [10, 0, 0], [0, 10, 0])
        tgc.create(db)

        # Create an ELL (Ellipsoid)
        # center=(0,0,100), vectors=(30,0,0), (0,30,0), (0,0,10)
        # This describes a flattened ellipsoid
        ell = ELL("my_ellipsoid", 
                  [0, 0, 100], 
                  [30, 0, 0], 
                  [0, 30, 0], 
                  [0, 0, 10])
        ell.create(db)

        # Create a combination including them
        comb = db.create_combination("advanced_assembly", members=[tgc, ell])
        
        # Add a sphere for comparison
        sph = Sphere("ref_sphere", radius=5).translate(0, 50, 25)
        sph.create(db)
        
        # Add another member to existing combination if we supported it, 
        # but our current create_combination API takes a list. 
        # Let's just recreate it with all 3.
        db.create_combination("advanced_assembly_full", members=[tgc, ell, sph])
        
    print("Database 'advanced.g' created successfully.")

if __name__ == "__main__":
    test_advanced_primitives()
