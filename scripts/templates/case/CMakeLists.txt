cmake_minimum_required(VERSION 3.16)
project(__TARGET__ CXX)

# samurai is resolved from the active environment or CMAKE_PREFIX_PATH.
find_package(samurai CONFIG REQUIRED)

add_executable(__TARGET__ main.cpp)
target_link_libraries(__TARGET__ PRIVATE samurai::samurai)
target_compile_features(__TARGET__ PRIVATE cxx_std_20)
