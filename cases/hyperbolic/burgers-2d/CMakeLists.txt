cmake_minimum_required(VERSION 3.16)
project(gallery-burgers-2d CXX)

find_package(samurai CONFIG REQUIRED)

add_executable(gallery-burgers-2d main.cpp)
target_link_libraries(gallery-burgers-2d PRIVATE samurai::samurai)
target_compile_features(gallery-burgers-2d PRIVATE cxx_std_20)
