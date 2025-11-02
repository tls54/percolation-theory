import type {
  HealthResponse,
  SimulationParams,
  SimulationResponse,
  SweepParams,
  SweepResponse,
  VisualizationParams,
  VisualizationStats,
} from '../types';

const API_BASE = 'http://localhost:8000';

export async function checkHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE}/api/health`);
  if (!response.ok) {
    throw new Error(`Health check failed: ${response.statusText}`);
  }
  return response.json();
}

export async function runSimulation(params: SimulationParams): Promise<SimulationResponse> {
  const response = await fetch(`${API_BASE}/api/simulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });

  if (!response.ok) {
    throw new Error(`Simulation failed: ${response.statusText}`);
  }

  return response.json();
}

export async function runSweep(params: SweepParams): Promise<SweepResponse> {
  const response = await fetch(`${API_BASE}/api/simulate/sweep`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });

  if (!response.ok) {
    throw new Error(`Sweep failed: ${response.statusText}`);
  }

  return response.json();
}

export async function getVisualization(params: VisualizationParams): Promise<{
  imageUrl: string;
  stats: VisualizationStats;
}> {
  const response = await fetch(`${API_BASE}/api/visualize/grid`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });

  if (!response.ok) {
    throw new Error(`Visualization failed: ${response.statusText}`);
  }

  const blob = await response.blob();
  const imageUrl = URL.createObjectURL(blob);

  const statsHeader = response.headers.get('X-Visualization-Stats');
  const stats = statsHeader ? JSON.parse(statsHeader) : {};

  return { imageUrl, stats };
}
