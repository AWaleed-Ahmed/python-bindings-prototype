import _brlcad
db = _brlcad.db_open("stage12_test.g", "r")
objs = _brlcad.list_objects(db)
print(f"Objects in DB: {objs}")
print(f"Type of objs: {type(objs)}")
if objs:
    print(f"First element type: {type(objs[0])}")
    print(f"First element value: '{objs[0]}'")
_brlcad.db_close(db)
