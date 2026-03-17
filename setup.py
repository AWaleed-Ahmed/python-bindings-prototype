from setuptools import setup, Extension
import os

# Define the C extension module
# In Stage 4b, we include all files from src/_brlcad/ and link to BRL-CAD libraries
brlcad_extension = Extension(
    "_brlcad",
    sources=[
        "src/_brlcad/module.c",
        "src/_brlcad/capsule_helpers.c",
        "src/_brlcad/db_bindings.c",  
        "src/_brlcad/comb_bindings.c",
        "src/_brlcad/transform_bindings.c",
        "src/_brlcad/advanced_primitive_bindings.c",
        "src/_brlcad/attribute_bindings.c",
        "src/adapter/db_adapter.c",   
        "src/adapter/primitive_adapter.c", 
        "src/adapter/comb_adapter.c",
        "src/adapter/transform_adapter.c",
        "src/adapter/advanced_primitive_adapter.c",
        "src/adapter/attribute_adapter.c",
    ],
    include_dirs=["src/_brlcad", "src/adapter", "/usr/local/include/brlcad"],
    libraries=["rt", "wdb", "bu"],
    library_dirs=["/usr/local/lib"],
    extra_compile_args=["-Wall", "-O0", "-g"], # Debug info and warnings
)

setup(
    name="pybrlcad",
    version="0.1.0",
    description="Python bindings for BRL-CAD",
    ext_modules=[brlcad_extension],
    package_dir={"": "src"},
    packages=["brlcad", "brlcad.primitives", "brlcad.combination"],
)
