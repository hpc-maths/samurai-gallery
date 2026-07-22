cmake_minimum_required(VERSION 3.16)
project(gallery-burgers-1d CXX)

find_package(samurai CONFIG REQUIRED)

add_executable(gallery-burgers-1d main.cpp)
target_link_libraries(gallery-burgers-1d PRIVATE samurai::samurai)
target_compile_features(gallery-burgers-1d PRIVATE cxx_std_20)
