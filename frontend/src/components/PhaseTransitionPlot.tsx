import { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ReferenceLine, ResponsiveContainer } from 'recharts';
import { Play, AlertCircle } from 'lucide-react';
import type { Algorithm, SweepResponse } from '../types';
import { runSweep } from '../services/api';

interface PhaseTransitionPlotProps {
  N: number;
  numTrials: number;
  algorithm: Algorithm;
}

export default function PhaseTransitionPlot({ N, numTrials, algorithm }: PhaseTransitionPlotProps) {
  const [pMin, setPMin] = useState(0.5);
  const [pMax, setPMax] = useState(0.7);
  const [pSteps, setPSteps] = useState(31);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sweepData, setSweepData] = useState<SweepResponse | null>(null);

  const handleRunSweep = async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await runSweep({
        p_min: pMin,
        p_max: pMax,
        p_steps: pSteps,
        N,
        num_trials: numTrials,
        estimate_pc: true,
        algorithm,
      });

      setSweepData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to run sweep');
    } finally {
      setLoading(false);
    }
  };

  const chartData = sweepData
    ? sweepData.p_values.map((p, i) => ({
        p: p,
        probability: sweepData.percolation_probabilities[i],
      }))
    : [];

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900">Phase Transition Analysis</h3>

      {/* Controls */}
      <div className="bg-gray-50 rounded-lg p-4 space-y-4">
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              p_min
            </label>
            <input
              type="number"
              min="0"
              max="0.8"
              step="0.01"
              value={pMin}
              onChange={(e) => setPMin(parseFloat(e.target.value))}
              disabled={loading}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              p_max
            </label>
            <input
              type="number"
              min="0.6"
              max="1"
              step="0.01"
              value={pMax}
              onChange={(e) => setPMax(parseFloat(e.target.value))}
              disabled={loading}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Steps
            </label>
            <input
              type="number"
              min="11"
              max="51"
              step="2"
              value={pSteps}
              onChange={(e) => setPSteps(parseInt(e.target.value))}
              disabled={loading}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50"
            />
          </div>
        </div>

        <button
          onClick={handleRunSweep}
          disabled={loading}
          className="w-full flex items-center justify-center gap-2 bg-blue-600 text-white px-4 py-3 rounded-lg font-medium hover:bg-blue-700 focus:ring-4 focus:ring-blue-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? (
            <>
              <div className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full" />
              Running Sweep...
            </>
          ) : (
            <>
              <Play className="h-5 w-5" />
              Run Parameter Sweep
            </>
          )}
        </button>

        {sweepData && (
          <div className="text-sm text-gray-600">
            Computation time: {(sweepData.total_computation_time_s * 1000).toFixed(1)} ms
          </div>
        )}
      </div>

      {/* Chart */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        {error ? (
          <div className="text-center text-red-600 py-8">
            <AlertCircle className="h-12 w-12 mx-auto mb-2" />
            <p>{error}</p>
          </div>
        ) : chartData.length > 0 ? (
          <div>
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 30 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="p"
                  label={{ value: 'Occupation Probability (p)', position: 'bottom', offset: 0 }}
                  domain={[pMin, pMax]}
                  type="number"
                  tickFormatter={(value) => value.toFixed(2)}
                />
                <YAxis
                  label={{ value: 'Percolation Probability P(p)', angle: -90, position: 'insideLeft' }}
                  domain={[0, 1]}
                  tickFormatter={(value) => value.toFixed(1)}
                />
                <Tooltip
                  formatter={(value: number) => value.toFixed(3)}
                  labelFormatter={(value) => `p = ${Number(value).toFixed(3)}`}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="probability"
                  stroke="#3B82F6"
                  strokeWidth={2}
                  dot={false}
                  name="P(p)"
                />
                {sweepData?.pc_estimate && (
                  <ReferenceLine
                    x={sweepData.pc_estimate}
                    stroke="#EF4444"
                    strokeDasharray="5 5"
                    label={{
                      value: `p_c ≈ ${sweepData.pc_estimate.toFixed(3)} ± ${(sweepData.pc_stderr || 0).toFixed(3)}`,
                      position: 'top',
                      fill: '#EF4444',
                      fontSize: 12,
                    }}
                  />
                )}
              </LineChart>
            </ResponsiveContainer>

            {sweepData?.pc_estimate && (
              <div className="mt-4 p-4 bg-red-50 rounded-lg border border-red-200">
                <h4 className="font-semibold text-red-900 mb-2">Critical Point Estimate</h4>
                <div className="text-sm space-y-1">
                  <p>
                    <span className="text-gray-700">p_c = </span>
                    <span className="font-semibold text-red-900">
                      {sweepData.pc_estimate.toFixed(3)} ± {(sweepData.pc_stderr || 0).toFixed(3)}
                    </span>
                  </p>
                  {sweepData.pc_error_percent !== undefined && (
                    <p>
                      <span className="text-gray-700">Error: </span>
                      <span className="font-semibold text-red-900">
                        {sweepData.pc_error_percent.toFixed(2)}%
                      </span>
                    </p>
                  )}
                  <p>
                    <span className="text-gray-700">Method: </span>
                    <span className="font-semibold text-red-900">Sigmoid Fit</span>
                  </p>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center text-gray-500 py-12">
            <p>Run a parameter sweep to see the phase transition plot</p>
          </div>
        )}
      </div>
    </div>
  );
}
