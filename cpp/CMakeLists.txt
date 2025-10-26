cmake_minimum_required(VERSION 3.15)
project(percolation_cpp)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Optimization flags
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -march=native -DNDEBUG")

# Find pybind11
find_package(pybind11 REQUIRED)

# Create Python module
pybind11_add_module(percolation_cpp 
    src/bindings.cpp
)

# Include directories
target_include_directories(percolation_cpp PRIVATE src)