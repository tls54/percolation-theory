export type Algorithm = 'bfs' | 'numba' | 'cpp';

export interface SimulationParams {
  p: number;
  N: number;
  num_trials: number;
  algorithm: Algorithm;
}

export interface SimulationResponse {
  p: number;
  N: number;
  num_trials: number;
  percolation_probability: number;
  num_percolating: number;
  mean_num_clusters: number;
  mean_cluster_size: number;
  mean_spanning_size: number;
  computation_time_ms: number;
  algorithm_used: string;
}

export interface SweepParams {
  p_min: number;
  p_max: number;
  p_steps: number;
  N: number;
  num_trials: number;
  estimate_pc: boolean;
  algorithm: Algorithm;
}

export interface SweepResponse {
  p_values: number[];
  percolation_probabilities: number[];
  mean_cluster_counts: number[];
  mean_cluster_sizes: number[];
  N: number;
  num_trials: number;
  algorithm_used: string;
  total_computation_time_s: number;
  pc_estimate?: number;
  pc_stderr?: number;
  pc_error_percent?: number;
}

export interface VisualizationParams {
  p: number;
  N: number;
  algorithm: Algorithm;
  seed?: number;
  min_cluster_size?: number | null;
  colormap?: string;
  image_size?: [number, number];
}

export interface VisualizationStats {
  total_clusters: number;
  spanning_clusters: number;
  [key: string]: any;
}

export interface HealthResponse {
  status: string;
  version: string;
  cpp_available: boolean;
  numba_available: boolean;
}
