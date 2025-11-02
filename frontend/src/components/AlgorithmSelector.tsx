import type { Algorithm } from '../types';

interface AlgorithmSelectorProps {
  selected: Algorithm;
  onChange: (algo: Algorithm) => void;
  cppAvailable: boolean;
}

const algorithms = [
  {
    value: 'bfs' as Algorithm,
    label: 'BFS',
    description: 'Breadth-First Search (Slow, baseline)',
    speed: 'Slow',
  },
  {
    value: 'numba' as Algorithm,
    label: 'Numba',
    description: 'Numba JIT (Fast, 50x speedup)',
    speed: 'Fast',
  },
  {
    value: 'cpp' as Algorithm,
    label: 'C++',
    description: 'C++ Extension (Fastest, 17x vs Numba)',
    speed: 'Fastest',
  },
];

export default function AlgorithmSelector({ selected, onChange, cppAvailable }: AlgorithmSelectorProps) {
  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">
        Algorithm
      </label>
      <div className="space-y-2">
        {algorithms.map((algo) => {
          const isDisabled = algo.value === 'cpp' && !cppAvailable;

          return (
            <label
              key={algo.value}
              className={`flex items-start p-3 border rounded-lg cursor-pointer transition-colors ${
                selected === algo.value
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-300 hover:border-gray-400'
              } ${isDisabled ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              <input
                type="radio"
                name="algorithm"
                value={algo.value}
                checked={selected === algo.value}
                onChange={(e) => onChange(e.target.value as Algorithm)}
                disabled={isDisabled}
                className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500"
              />
              <div className="ml-3 flex-1">
                <div className="flex items-center justify-between">
                  <span className="font-medium text-gray-900">{algo.label}</span>
                  <span
                    className={`text-xs px-2 py-1 rounded ${
                      algo.speed === 'Fastest'
                        ? 'bg-green-100 text-green-800'
                        : algo.speed === 'Fast'
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {algo.speed}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mt-1">
                  {algo.description}
                  {isDisabled && ' (Not available)'}
                </p>
              </div>
            </label>
          );
        })}
      </div>
    </div>
  );
}
