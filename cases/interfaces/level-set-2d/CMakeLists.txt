cmake_minimum_required(VERSION 3.16)
project(gallery-level-set-2d CXX)

find_package(samurai CONFIG REQUIRED)

# main.cpp includes the vendored level_set_operators.hpp from this directory.
add_executable(gallery-level-set-2d main.cpp)
target_link_libraries(gallery-level-set-2d PRIVATE samurai::samurai)
target_compile_features(gallery-level-set-2d PRIVATE cxx_std_20)
