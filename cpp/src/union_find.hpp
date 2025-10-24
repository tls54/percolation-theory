#pragma once
#include <vector>
#include <cstdint>

namespace percolation {

class UnionFind {
private:
    std::vector<int32_t> parent;
    std::vector<int32_t> rank;
    
    // Inline find with path compression
    inline int32_t find(int32_t x) {
        if (parent[x] != x) {
            parent[x] = find(parent[x]);  // Path compression
        }
        return parent[x];
    }
    
    // Inline union by rank
    inline void unite(int32_t x, int32_t y) {
        int32_t root_x = find(x);
        int32_t root_y = find(y);
        
        if (root_x == root_y) return;
        
        // Union by rank
        if (rank[root_x] < rank[root_y]) {
            parent[root_x] = root_y;
        } else if (rank[root_x] > rank[root_y]) {
            parent[root_y] = root_x;
        } else {
            parent[root_y] = root_x;
            rank[root_x]++;
        }
    }

public:
    UnionFind(int32_t size) : parent(size), rank(size, 0) {
        for (int32_t i = 0; i < size; i++) {
            parent[i] = i;
        }
    }
    
    // Main algorithm: returns labels array
    std::vector<int32_t> find_clusters(const std::vector<bool>& grid, int32_t N) {
        std::vector<int32_t> labels(N * N, 0);
        
        // First pass: merge clusters
        for (int32_t i = 0; i < N; i++) {
            for (int32_t j = 0; j < N; j++) {
                if (!grid[i * N + j]) continue;
                
                int32_t current = i * N + j;
                
                // Check left neighbor
                if (j > 0 && grid[i * N + (j - 1)]) {
                    unite(current, current - 1);
                }
                
                // Check up neighbor
                if (i > 0 && grid[(i - 1) * N + j]) {
                    unite(current, current - N);
                }
            }
        }
        
        // Second pass: assign cluster labels
        std::vector<int32_t> cluster_map(N * N, -1);
        int32_t next_label = 1;
        
        for (int32_t i = 0; i < N; i++) {
            for (int32_t j = 0; j < N; j++) {
                if (!grid[i * N + j]) continue;
                
                int32_t current = i * N + j;
                int32_t root = find(current);
                
                if (cluster_map[root] == -1) {
                    cluster_map[root] = next_label++;
                }
                
                labels[i * N + j] = cluster_map[root];
            }
        }
        
        return labels;
    }
};

} // namespace percolation