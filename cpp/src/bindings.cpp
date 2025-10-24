#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include "union_find.hpp"

namespace py = pybind11;

// Python-facing function that handles NumPy arrays
py::array_t<int32_t> find_clusters_cpp(py::array_t<bool> grid_array) {
    // Get buffer info
    py::buffer_info buf = grid_array.request();
    
    if (buf.ndim != 2) {
        throw std::runtime_error("Grid must be 2-dimensional");
    }
    
    int32_t N = buf.shape[0];
    if (buf.shape[1] != N) {
        throw std::runtime_error("Grid must be square (N×N)");
    }
    
    // Convert NumPy array to std::vector
    bool* ptr = static_cast<bool*>(buf.ptr);
    std::vector<bool> grid(ptr, ptr + N * N);
    
    // Run algorithm
    percolation::UnionFind uf(N * N);
    std::vector<int32_t> labels = uf.find_clusters(grid, N);
    
    // Convert back to NumPy array (2D)
    py::array_t<int32_t> result({N, N});
    auto result_buf = result.request();
    int32_t* result_ptr = static_cast<int32_t*>(result_buf.ptr);
    
    std::copy(labels.begin(), labels.end(), result_ptr);
    
    return result;
}

PYBIND11_MODULE(percolation_cpp, m) {
    m.doc() = "Fast C++ percolation algorithms";
    
    m.def("find_clusters", &find_clusters_cpp,
          "Find clusters using Union-Find algorithm (C++)",
          py::arg("grid"));
}