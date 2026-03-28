cmake_minimum_required(VERSION 3.18)
project(pybrlcad_moose_bridge LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(MOOSE_ROOT "${CMAKE_SOURCE_DIR}/../../third_party/MOOSE" CACHE PATH "Path to BRL-CAD/MOOSE source tree")
set(MOOSE_BUILD "${MOOSE_ROOT}/build" CACHE PATH "Path to BRL-CAD/MOOSE build tree")

include_directories(
    ${MOOSE_ROOT}/include
)

link_directories(
    ${MOOSE_BUILD}/src
)

add_library(brlcad_moose_bridge SHARED moose_c_api.cpp)

if (MSVC)
    target_compile_definitions(brlcad_moose_bridge PRIVATE BRLCAD_MOOSE_EXPORT=__declspec(dllimport))
else()
    target_compile_definitions(brlcad_moose_bridge PRIVATE BRLCAD_MOOSE_EXPORT=)
endif()

target_include_directories(brlcad_moose_bridge PRIVATE ${MOOSE_ROOT}/include)

# MOOSE builds a shared library named "brlcad" by default.
# This bridge links against that library and exposes a C ABI.
target_link_libraries(brlcad_moose_bridge PRIVATE brlcad)

set_target_properties(brlcad_moose_bridge PROPERTIES
    OUTPUT_NAME "brlcad_moose_bridge"
    PREFIX "lib"
)
