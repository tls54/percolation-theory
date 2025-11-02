import { BarChart3, Grid3x3, Clock, TrendingUp, Layers, Maximize2 } from 'lucide-react';
import type { SimulationResponse } from '../types';

interface SimulationResultsProps {
  results: SimulationResponse | null;
}

export default function SimulationResults({ results }: SimulationResultsProps) {
  if (!results) {
    return null;
  }

  const percolationPercent = (results.percolation_probability * 100).toFixed(1);
  const isPercolating = results.percolation_probability > 0.5;

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Results</h2>

      <div className="grid grid-cols-2 gap-4">
        {/* Percolation Probability */}
        <div
          className={`col-span-2 p-4 rounded-lg ${
            isPercolating ? 'bg-green-50 border border-green-200' : 'bg-gray-50 border border-gray-200'
          }`}
        >
          <div className="flex items-center gap-2 mb-1">
            <TrendingUp className={`h-5 w-5 ${isPercolating ? 'text-green-600' : 'text-gray-600'}`} />
            <span className="text-sm font-medium text-gray-700">Percolation Probability</span>
          </div>
          <div className={`text-3xl font-bold ${isPercolating ? 'text-green-600' : 'text-gray-600'}`}>
            {percolationPercent}%
          </div>
          <div className="text-sm text-gray-600 mt-1">
            {results.num_percolating} / {results.num_trials} trials percolated
          </div>
        </div>

        {/* Mean Number of Clusters */}
        <div className="col-span-2 p-4 bg-indigo-50 rounded-lg border border-indigo-200">
          <div className="flex items-center gap-2 mb-1">
            <Layers className="h-5 w-5 text-indigo-600" />
            <span className="text-sm font-medium text-gray-700">Mean Number of Clusters</span>
          </div>
          <div className="text-2xl font-bold text-indigo-600">
            {results.mean_num_clusters.toFixed(1)}
          </div>
        </div>

        {/* Mean Cluster Size */}
        <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
          <div className="flex items-center gap-2 mb-1">
            <BarChart3 className="h-5 w-5 text-blue-600" />
            <span className="text-sm font-medium text-gray-700">Cluster Size</span>
          </div>
          <div className="text-xl font-bold text-blue-600">
            {results.mean_cluster_size.toFixed(1)}
          </div>
          <div className="text-xs text-gray-600">avg</div>
        </div>

        {/* Mean Spanning Size */}
        <div className="p-4 bg-teal-50 rounded-lg border border-teal-200">
          <div className="flex items-center gap-2 mb-1">
            <Maximize2 className="h-5 w-5 text-teal-600" />
            <span className="text-sm font-medium text-gray-700">Spanning Size</span>
          </div>
          <div className="text-xl font-bold text-teal-600">
            {results.mean_spanning_size.toFixed(1)}
          </div>
          <div className="text-xs text-gray-600">avg</div>
        </div>

        {/* Grid Info */}
        <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
          <div className="flex items-center gap-2 mb-1">
            <Grid3x3 className="h-5 w-5 text-purple-600" />
            <span className="text-sm font-medium text-gray-700">Grid Size</span>
          </div>
          <div className="text-xl font-bold text-purple-600">
            {results.N} × {results.N}
          </div>
          <div className="text-xs text-gray-600">
            p = {results.p.toFixed(3)}
          </div>
        </div>

        {/* Computation Time */}
        <div className="p-4 bg-orange-50 rounded-lg border border-orange-200">
          <div className="flex items-center gap-2 mb-1">
            <Clock className="h-5 w-5 text-orange-600" />
            <span className="text-sm font-medium text-gray-700">Time</span>
          </div>
          <div className="text-xl font-bold text-orange-600">
            {results.computation_time_ms.toFixed(1)} ms
          </div>
          <div className="text-xs text-gray-600">
            {results.algorithm_used}
          </div>
        </div>
      </div>
    </div>
  );
}
