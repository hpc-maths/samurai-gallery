cmake_minimum_required(VERSION 3.16)
project(gallery-advection-2d CXX)

# Every gallery case depends on samurai through its installed CMake config.
# It is resolved from the active environment (conda/micromamba) or from any
# path added to CMAKE_PREFIX_PATH. No case ever vendors samurai itself.
find_package(samurai CONFIG REQUIRED)

add_executable(gallery-advection-2d main.cpp)
target_link_libraries(gallery-advection-2d PRIVATE samurai::samurai)
target_compile_features(gallery-advection-2d PRIVATE cxx_std_20)
