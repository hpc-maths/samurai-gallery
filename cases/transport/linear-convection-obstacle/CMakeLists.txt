cmake_minimum_required(VERSION 3.16)
project(gallery-linear-convection-obstacle CXX)

find_package(samurai CONFIG REQUIRED)

add_executable(gallery-linear-convection-obstacle main.cpp)
target_link_libraries(gallery-linear-convection-obstacle PRIVATE samurai::samurai)
target_compile_features(gallery-linear-convection-obstacle PRIVATE cxx_std_20)
