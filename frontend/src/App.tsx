import { useState, useEffect } from 'react';
import type { SimulationParams, SimulationResponse } from './types';
import { checkHealth, runSimulation } from './services/api';
import ParameterControls from './components/ParameterControls';
import SimulationResults from './components/SimulationResults';
import GridVisualization from './components/GridVisualization';
import PhaseTransitionPlot from './components/PhaseTransitionPlot';

type TabType = 'grid' | 'transition';

function App() {
  const [params, setParams] = useState<SimulationParams>({
    p: 0.59,
    N: 50,
    num_trials: 100,
    algorithm: 'cpp',
  });

  const [results, setResults] = useState<SimulationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<TabType>('grid');
  const [cppAvailable, setCppAvailable] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Check health on mount
  useEffect(() => {
    checkHealth()
      .then((health) => {
        setCppAvailable(health.cpp_available);
        if (!health.cpp_available && params.algorithm === 'cpp') {
          setParams({ ...params, algorithm: 'numba' });
        }
      })
      .catch((err) => {
        console.error('Health check failed:', err);
        setError('Failed to connect to backend API. Please ensure it is running on http://localhost:8000');
      });
  }, []);

  const handleSimulate = async (newParams: SimulationParams) => {
    console.log('Starting simulation with params:', newParams);
    setLoading(true);
    setError(null);

    try {
      const result = await runSimulation(newParams);
      console.log('Simulation result:', result);
      setResults(result);
      setParams(newParams);
    } catch (err) {
      console.error('Simulation failed:', err);
      setError(err instanceof Error ? err.message : 'Simulation failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900">
            Percolation Theory Simulator
          </h1>
          <p className="mt-1 text-sm text-gray-600">
            Interactive visualization and analysis of percolation phase transitions
          </p>
        </div>
      </header>

      {/* Error Banner */}
      {error && (
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800">{error}</p>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
          {/* Left Column - Controls and Results */}
          <div className="lg:col-span-2 space-y-6">
            <ParameterControls
              onSimulate={handleSimulate}
              isLoading={loading}
              cppAvailable={cppAvailable}
            />

            {results && <SimulationResults results={results} />}
          </div>

          {/* Right Column - Visualizations */}
          <div className="lg:col-span-3">
            <div className="bg-white rounded-lg shadow">
              {/* Tabs */}
              <div className="border-b border-gray-200 px-6 pt-6">
                <nav className="-mb-px flex space-x-8">
                  <button
                    onClick={() => setActiveTab('grid')}
                    className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                      activeTab === 'grid'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    Grid View
                  </button>
                  <button
                    onClick={() => setActiveTab('transition')}
                    className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                      activeTab === 'transition'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    Phase Transition
                  </button>
                </nav>
              </div>

              {/* Tab Content */}
              <div className="p-6">
                {activeTab === 'grid' ? (
                  <GridVisualization params={params} />
                ) : (
                  <PhaseTransitionPlot
                    N={params.N}
                    numTrials={params.num_trials}
                    algorithm={params.algorithm}
                  />
                )}
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="max-w-7xl mx-auto px-4 py-8 mt-12 border-t border-gray-200">
        <p className="text-center text-sm text-gray-600">
          Percolation Theory Simulator - Interactive phase transition analysis
        </p>
      </footer>
    </div>
  );
}

export default App;
