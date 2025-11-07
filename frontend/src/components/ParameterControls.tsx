import { useState } from 'react';
import { Play, Info } from 'lucide-react';
import type { SimulationParams, Algorithm } from '../types';
import AlgorithmSelector from './AlgorithmSelector';

interface ParameterControlsProps {
  initialParams: SimulationParams;
  onParamsChange: (params: SimulationParams) => void;
  onSimulate: (params: SimulationParams) => void;
  isLoading: boolean;
  cppAvailable: boolean;
}

export default function ParameterControls({
  initialParams,
  onParamsChange,
  onSimulate,
  isLoading,
  cppAvailable
}: ParameterControlsProps) {
  const [p, setP] = useState(initialParams.p);
  const [N, setN] = useState(initialParams.N);
  const [numTrials, setNumTrials] = useState(initialParams.num_trials);
  const [algorithm, setAlgorithm] = useState<Algorithm>(initialParams.algorithm);

  const updateParams = (newP: number, newN: number, newNumTrials: number, newAlgorithm: Algorithm) => {
    onParamsChange({ p: newP, N: newN, num_trials: newNumTrials, algorithm: newAlgorithm });
  };

  const handlePChange = (newP: number) => {
    setP(newP);
    updateParams(newP, N, numTrials, algorithm);
  };

  const handleNChange = (newN: number) => {
    setN(newN);
    updateParams(p, newN, numTrials, algorithm);
  };

  const handleNumTrialsChange = (newNumTrials: number) => {
    setNumTrials(newNumTrials);
    updateParams(p, N, newNumTrials, algorithm);
  };

  const handleAlgorithmChange = (newAlgorithm: Algorithm) => {
    setAlgorithm(newAlgorithm);
    updateParams(p, N, numTrials, newAlgorithm);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSimulate({ p, N, num_trials: numTrials, algorithm });
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Simulation Parameters</h2>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Occupation Probability (p) */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="block text-sm font-medium text-gray-700">
              Occupation Probability (p)
            </label>
            <span className="text-sm font-semibold text-blue-600">{p.toFixed(4)}</span>
          </div>
          <input
            type="range"
            min="0"
            max="1"
            step="0.001"
            value={p}
            onChange={(e) => handlePChange(parseFloat(e.target.value))}
            disabled={isLoading}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600 disabled:opacity-50"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>0.0</span>
            <span>1.0</span>
          </div>
          <input
            type="number"
            min="0"
            max="1"
            step="0.0001"
            value={p}
            onChange={(e) => handlePChange(parseFloat(e.target.value))}
            disabled={isLoading}
            className="mt-2 w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50"
          />
          <div className="text-xs text-gray-500 mt-1">
            Supports up to 4 decimal places for precise control
          </div>
        </div>

        {/* Grid Size (N) */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <label className="block text-sm font-medium text-gray-700">
                Grid Size (N)
              </label>
              <div className="group relative">
                <Info className="h-4 w-4 text-gray-400 cursor-help" />
                <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
                  Larger grids take longer to compute
                </div>
              </div>
            </div>
            <span className="text-sm font-semibold text-blue-600">{N}</span>
          </div>
          <input
            type="range"
            min="10"
            max="500"
            step="10"
            value={N}
            onChange={(e) => handleNChange(parseInt(e.target.value))}
            disabled={isLoading}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600 disabled:opacity-50"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>10</span>
            <span>500</span>
          </div>
          <input
            type="number"
            min="10"
            max="500"
            step="10"
            value={N}
            onChange={(e) => handleNChange(parseInt(e.target.value))}
            disabled={isLoading}
            className="mt-2 w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50"
          />
        </div>

        {/* Number of Trials */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="block text-sm font-medium text-gray-700">
              Number of Trials
            </label>
            <span className="text-sm font-semibold text-blue-600">{numTrials}</span>
          </div>
          <input
            type="range"
            min="10"
            max="500"
            step="10"
            value={numTrials}
            onChange={(e) => handleNumTrialsChange(parseInt(e.target.value))}
            disabled={isLoading}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600 disabled:opacity-50"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>10</span>
            <span>500</span>
          </div>
          <input
            type="number"
            min="10"
            max="500"
            step="10"
            value={numTrials}
            onChange={(e) => handleNumTrialsChange(parseInt(e.target.value))}
            disabled={isLoading}
            className="mt-2 w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50"
          />
        </div>

        {/* Algorithm Selector */}
        <AlgorithmSelector
          selected={algorithm}
          onChange={handleAlgorithmChange}
          cppAvailable={cppAvailable}
        />

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading}
          className="w-full flex items-center justify-center gap-2 bg-blue-600 text-white px-4 py-3 rounded-lg font-medium hover:bg-blue-700 focus:ring-4 focus:ring-blue-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isLoading ? (
            <>
              <div className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full" />
              Running Simulation...
            </>
          ) : (
            <>
              <Play className="h-5 w-5" />
              Run Simulation
            </>
          )}
        </button>
      </form>
    </div>
  );
}
