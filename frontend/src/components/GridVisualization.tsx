import { useState, useEffect } from 'react';
import { Download, AlertCircle } from 'lucide-react';
import type { SimulationParams, VisualizationStats } from '../types';
import { getVisualization } from '../services/api';

interface GridVisualizationProps {
  params: SimulationParams;
  autoRefresh?: boolean;
}

export default function GridVisualization({ params, autoRefresh = false }: GridVisualizationProps) {
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [stats, setStats] = useState<VisualizationStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    let oldImageUrl: string | null = null;

    const fetchVisualization = async () => {
      setLoading(true);
      setError(null);

      try {
        const result = await getVisualization({
          p: params.p,
          N: params.N,
          algorithm: params.algorithm,
        });

        if (mounted) {
          // Revoke old URL to prevent memory leaks
          if (oldImageUrl) {
            URL.revokeObjectURL(oldImageUrl);
          }
          oldImageUrl = result.imageUrl;

          console.log('Visualization stats received:', result.stats);
          setImageUrl(result.imageUrl);
          setStats(result.stats);
        }
      } catch (err) {
        if (mounted) {
          setError(err instanceof Error ? err.message : 'Failed to load visualization');
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };

    if (autoRefresh) {
      fetchVisualization();
    }

    return () => {
      mounted = false;
      if (oldImageUrl) {
        URL.revokeObjectURL(oldImageUrl);
      }
    };
  }, [params.p, params.N, params.algorithm, autoRefresh]);

  const handleGenerate = () => {
    setLoading(true);
    setError(null);

    getVisualization({
      p: params.p,
      N: params.N,
      algorithm: params.algorithm,
    })
      .then((result) => {
        // Revoke old URL to prevent memory leaks
        if (imageUrl) {
          URL.revokeObjectURL(imageUrl);
        }

        console.log('Visualization stats received:', result.stats);
        setImageUrl(result.imageUrl);
        setStats(result.stats);
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : 'Failed to load visualization');
      })
      .finally(() => {
        setLoading(false);
      });
  };

  const handleDownload = () => {
    if (imageUrl) {
      const a = document.createElement('a');
      a.href = imageUrl;
      a.download = `percolation_p${params.p}_N${params.N}.png`;
      a.click();
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Grid Visualization</h3>
        <div className="flex gap-2">
          {imageUrl && (
            <button
              onClick={handleDownload}
              className="flex items-center gap-2 px-3 py-2 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors"
            >
              <Download className="h-4 w-4" />
              Download
            </button>
          )}
          <button
            onClick={handleGenerate}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Generating...' : 'Generate Grid'}
          </button>
        </div>
      </div>

      <div className="bg-gray-50 rounded-lg p-4 min-h-[400px] flex items-center justify-center">
        {loading ? (
          <div className="text-center">
            <div className="animate-spin h-12 w-12 border-4 border-blue-600 border-t-transparent rounded-full mx-auto mb-4" />
            <p className="text-gray-600">Generating visualization...</p>
          </div>
        ) : error ? (
          <div className="text-center text-red-600">
            <AlertCircle className="h-12 w-12 mx-auto mb-2" />
            <p>{error}</p>
          </div>
        ) : imageUrl ? (
          <div className="w-full">
            <img
              src={imageUrl}
              alt="Percolation Grid"
              className="w-full h-auto rounded-lg border border-gray-300"
            />
          </div>
        ) : (
          <div className="text-center text-gray-500">
            <p>Click "Generate Grid" to visualize the percolation grid</p>
          </div>
        )}
      </div>

      {stats && (
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h4 className="font-semibold text-gray-900 mb-3">Visualization Statistics</h4>
          <div className="grid grid-cols-2 gap-3 text-sm">
            {/* Grid Parameters */}
            <div className="col-span-2 pb-2 border-b border-gray-200">
              <span className="text-gray-600">Grid:</span>
              <span className="ml-2 font-semibold text-gray-900">
                {params.N} × {params.N}
              </span>
            </div>
            <div className="col-span-2">
              <span className="text-gray-600">Occupation Probability:</span>
              <span className="ml-2 font-semibold text-gray-900">p = {params.p.toFixed(4)}</span>
            </div>
            <div className="col-span-2">
              <span className="text-gray-600">Algorithm:</span>
              <span className="ml-2 font-semibold text-gray-900">{params.algorithm.toUpperCase()}</span>
            </div>

            {/* Cluster Statistics */}
            <div className="col-span-2 pt-2 border-t border-gray-200">
              <span className="text-gray-600 font-medium">Cluster Analysis</span>
            </div>
            <div>
              <span className="text-gray-600">Total Clusters:</span>
              <span className="ml-2 font-semibold text-gray-900">{stats.total_clusters ?? 0}</span>
            </div>
            <div>
              <span className="text-gray-600">Colored Clusters:</span>
              <span className="ml-2 font-semibold text-gray-900">{stats.colored_clusters ?? 0}</span>
            </div>
            <div>
              <span className="text-gray-600">Spanning Clusters:</span>
              <span
                className={`ml-2 font-semibold ${
                  (stats.spanning_clusters ?? 0) > 0 ? 'text-green-600' : 'text-gray-900'
                }`}
              >
                {stats.spanning_clusters ?? 0}
              </span>
            </div>
            <div>
              <span className="text-gray-600">Large Clusters:</span>
              <span className="ml-2 font-semibold text-gray-900">{stats.large_clusters ?? 0}</span>
            </div>
            <div>
              <span className="text-gray-600">Small Clusters:</span>
              <span className="ml-2 font-semibold text-gray-900">{stats.small_clusters ?? 0}</span>
            </div>
            <div>
              <span className="text-gray-600">Min Size Threshold:</span>
              <span className="ml-2 font-semibold text-gray-900">{stats.min_size_threshold ?? 0}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
