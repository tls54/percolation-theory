# Percolation Theory - Frontend Implementation Guide

## Project Overview
Build a React frontend for an existing percolation theory simulation API. The backend is complete and running - this document specifies the frontend requirements.

## Backend API (Already Running)

**Base URL:** `http://localhost:8000`

**Available Endpoints:**

1. **Health Check**
   ```
   GET /api/health
   Response: {
     "status": "healthy",
     "version": "0.1.0",
     "cpp_available": true,
     "numba_available": true
   }
   ```

2. **Single Simulation**
   ```
   POST /api/simulate
   Request: {
     "p": 0.6,              // 0.0-1.0
     "N": 50,               // 10-500
     "num_trials": 100,     // 1-1000
     "algorithm": "cpp"     // "bfs", "numba", or "cpp"
   }
   Response: {
     "p": 0.6,
     "N": 50,
     "num_trials": 100,
     "percolation_probability": 0.73,
     "num_percolating": 73,
     "mean_cluster_size": 124.5,
     "std_cluster_size": 45.2,
     "computation_time_ms": 15.3,
     "algorithm_used": "cpp"
   }
   ```

3. **Parameter Sweep (for phase transition)**
   ```
   POST /api/simulate/sweep
   Request: {
     "p_min": 0.5,
     "p_max": 0.7,
     "p_steps": 31,
     "N": 50,
     "num_trials": 100,
     "estimate_pc": true,
     "algorithm": "cpp"
   }
   Response: {
     "p_values": [0.5, 0.51, ...],
     "percolation_probabilities": [0.02, 0.05, ...],
     "mean_cluster_sizes": [2.3, 3.1, ...],
     "computation_time_ms": 234.5,
     "pc_estimate": {
       "value": 0.593,
       "uncertainty": 0.003,
       "method": "sigmoid_fit"
     }
   }
   ```

4. **Grid Visualization**
   ```
   POST /api/visualize/grid
   Request: {
     "p": 0.6,
     "N": 100,
     "algorithm": "cpp",
     "seed": 42,                    // optional, for reproducibility
     "min_cluster_size": null,      // null = auto
     "colormap": "tab20",
     "image_size": [800, 800]
   }
   Response: PNG image (binary)
   Headers: {
     "X-Visualization-Stats": "{\"total_clusters\": 2143, \"spanning_clusters\": 1, ...}"
   }
   ```

**API Documentation:** Available at `http://localhost:8000/docs` (interactive Swagger UI)

---

## Frontend Requirements

### Technology Stack
- **Framework:** React 18+ with TypeScript
- **Build Tool:** Vite
- **Styling:** Tailwind CSS
- **Charting:** Recharts (for phase transition plot)
- **Icons:** Lucide React
- **HTTP Client:** fetch API (native)

### Project Structure
```
frontend/
├── src/
│   ├── components/
│   │   ├── ParameterControls.tsx    // Input controls
│   │   ├── GridVisualization.tsx    // Display grid PNG
│   │   ├── PhaseTransitionPlot.tsx  // Recharts plot
│   │   ├── SimulationResults.tsx    // Stats display
│   │   └── AlgorithmSelector.tsx    // BFS/Numba/C++ picker
│   ├── services/
│   │   └── api.ts                   // API client functions
│   ├── types/
│   │   └── index.ts                 // TypeScript interfaces
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

---

## UI Design Specification

### Layout
Two-column responsive layout:

**Left Column (40%):** Controls and Results
- Parameter controls (sliders/inputs)
- Algorithm selector
- Run simulation button
- Statistics display

**Right Column (60%):** Visualizations
- Tabs: "Grid View" | "Phase Transition"
- Grid View: Display PNG from API
- Phase Transition: Interactive Recharts plot

### Color Scheme
- **Primary:** Blue (#3B82F6)
- **Success:** Green (#10B981)
- **Warning:** Orange (#F59E0B)
- **Background:** White/Gray-50
- **Dark Mode:** Optional (nice to have)

---

## Component Specifications

### 1. ParameterControls.tsx

**Purpose:** Input controls for simulation parameters

**UI Elements:**
- **Occupation Probability (p):** 
  - Slider (0.0 - 1.0, step 0.01)
  - Number input
  - Default: 0.593 (near critical point)
  
- **Grid Size (N):**
  - Slider (10 - 200, step 10)
  - Number input  
  - Default: 50
  - Info tooltip: "Larger grids take longer"
  
- **Number of Trials:**
  - Slider (10 - 500, step 10)
  - Number input
  - Default: 100
  
- **Algorithm Selector:**
  - Radio buttons or dropdown
  - Options: BFS, Numba, C++
  - Show speed indicator (C++ fastest)
  - Default: cpp

**Props:**
```typescript
interface ParameterControlsProps {
  onSimulate: (params: SimulationParams) => void;
  isLoading: boolean;
}
```

**Behavior:**
- Validate inputs (use API constraints)
- Disable controls while loading
- Show "Run Simulation" button
- Indicate loading state with spinner

---

### 2. GridVisualization.tsx

**Purpose:** Display cluster visualization PNG from API

**Features:**
- Display image from `/api/visualize/grid`
- Show loading spinner while fetching
- Parse and display stats from `X-Visualization-Stats` header
- Show metadata: N, p, algorithm used
- Optional: Click to download PNG

**Stats Display (from header):**
- Total clusters
- Spanning clusters (highlight if > 0)
- Large clusters colored
- Small clusters (gray)

**Props:**
```typescript
interface GridVisualizationProps {
  params: SimulationParams;
  autoRefresh?: boolean;
}
```

**Implementation Note:**
- Fetch image as blob: `fetch(...).then(r => r.blob())`
- Create object URL: `URL.createObjectURL(blob)`
- Remember to revoke old URLs to prevent memory leaks

---

### 3. PhaseTransitionPlot.tsx

**Purpose:** Interactive plot of P(p) vs p using Recharts

**Data Source:** `/api/simulate/sweep`

**UI Elements:**
- Line chart: x = p, y = percolation probability
- Mark p_c with vertical dashed line (red)
- Show p_c value in legend
- Tooltip on hover showing exact values
- Responsive sizing

**Controls:**
- **p_min:** Input (0.0 - 0.8, default 0.5)
- **p_max:** Input (0.6 - 1.0, default 0.7)
- **Steps:** Slider (11 - 51, default 31)
- **Run Sweep** button

**Recharts Configuration:**
```typescript
<LineChart width={600} height={400} data={chartData}>
  <CartesianGrid strokeDasharray="3 3" />
  <XAxis 
    dataKey="p" 
    label={{value: 'Occupation Probability (p)', position: 'bottom'}}
    domain={[p_min, p_max]}
  />
  <YAxis 
    label={{value: 'Percolation Probability P(p)', angle: -90, position: 'left'}}
    domain={[0, 1]}
  />
  <Tooltip formatter={(value: number) => value.toFixed(3)} />
  <Legend />
  <Line 
    type="monotone" 
    dataKey="probability" 
    stroke="#3B82F6" 
    strokeWidth={2}
    dot={false}
    name="P(p)"
  />
  {pc && (
    <ReferenceLine 
      x={pc.value} 
      stroke="#EF4444" 
      strokeDasharray="5 5"
      label={`p_c ≈ ${pc.value.toFixed(3)} ± ${pc.uncertainty.toFixed(3)}`}
    />
  )}
</LineChart>
```

**Props:**
```typescript
interface PhaseTransitionPlotProps {
  N: number;
  numTrials: number;
  algorithm: string;
}
```

---

### 4. SimulationResults.tsx

**Purpose:** Display statistics from simulation

**Layout:** Card-based grid

**Metrics to Display:**
1. **Percolation Probability**
   - Large, prominent
   - Color: Green if > 0.5, Gray otherwise
   - Format: "73.0%"

2. **Trials Percolating**
   - "73 / 100 percolated"

3. **Mean Cluster Size**
   - With standard deviation
   - Format: "124.5 ± 45.2"

4. **Computation Time**
   - Format: "15.3 ms"
   - Show algorithm used

5. **Grid Info**
   - N × N = total sites
   - p value used

**Props:**
```typescript
interface SimulationResultsProps {
  results: SimulationResponse | null;
}
```

**Visual Design:**
- Use cards/boxes for each metric
- Icons from lucide-react
- Responsive grid (2 columns on mobile, 3+ on desktop)

---

### 5. AlgorithmSelector.tsx

**Purpose:** Choose simulation algorithm

**UI:**
- Radio button group or segmented control
- Options:
  1. **BFS** - "Breadth-First Search (Slow, baseline)"
  2. **Numba** - "Numba JIT (Fast, 50x speedup)"
  3. **C++** - "C++ Extension (Fastest, 17x vs Numba)" [if available]

**Features:**
- Check `/api/health` on mount to see if C++ available
- Disable C++ option if `cpp_available: false`
- Show tooltip with performance info on hover

**Props:**
```typescript
interface AlgorithmSelectorProps {
  selected: Algorithm;
  onChange: (algo: Algorithm) => void;
  cppAvailable: boolean;
}
```

---

## API Service (api.ts)

Create typed API client functions:

```typescript
export interface SimulationParams {
  p: number;
  N: number;
  num_trials: number;
  algorithm: 'bfs' | 'numba' | 'cpp';
}

export interface SimulationResponse {
  p: number;
  N: number;
  num_trials: number;
  percolation_probability: number;
  num_percolating: number;
  mean_cluster_size: number;
  std_cluster_size: number;
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
  algorithm: 'bfs' | 'numba' | 'cpp';
}

export interface SweepResponse {
  p_values: number[];
  percolation_probabilities: number[];
  mean_cluster_sizes: number[];
  computation_time_ms: number;
  pc_estimate?: {
    value: number;
    uncertainty: number;
    method: string;
  };
}

export interface VisualizationParams {
  p: number;
  N: number;
  algorithm: 'bfs' | 'numba' | 'cpp';
  seed?: number;
  min_cluster_size?: number | null;
  colormap?: string;
  image_size?: [number, number];
}

export interface HealthResponse {
  status: string;
  version: string;
  cpp_available: boolean;
  numba_available: boolean;
}

const API_BASE = 'http://localhost:8000';

export async function checkHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE}/api/health`);
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
  stats: any;
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
```

---

## App.tsx Structure

```typescript
function App() {
  const [params, setParams] = useState<SimulationParams>({
    p: 0.593,
    N: 50,
    num_trials: 100,
    algorithm: 'cpp'
  });
  
  const [results, setResults] = useState<SimulationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'grid' | 'transition'>('grid');
  const [cppAvailable, setCppAvailable] = useState(true);
  
  // Check health on mount
  useEffect(() => {
    checkHealth().then(health => {
      setCppAvailable(health.cpp_available);
      if (!health.cpp_available && params.algorithm === 'cpp') {
        setParams({...params, algorithm: 'numba'});
      }
    });
  }, []);
  
  const handleSimulate = async (newParams: SimulationParams) => {
    setLoading(true);
    try {
      const result = await runSimulation(newParams);
      setResults(result);
      setParams(newParams);
    } catch (error) {
      console.error('Simulation failed:', error);
      // Show error toast/notification
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900">
            Percolation Theory Simulator
          </h1>
        </div>
      </header>
      
      <main className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
          {/* Left Column - Controls */}
          <div className="lg:col-span-2 space-y-6">
            <ParameterControls 
              onSimulate={handleSimulate}
              isLoading={loading}
            />
            
            {results && (
              <SimulationResults results={results} />
            )}
          </div>
          
          {/* Right Column - Visualizations */}
          <div className="lg:col-span-3">
            <div className="bg-white rounded-lg shadow p-6">
              {/* Tabs */}
              <div className="border-b border-gray-200 mb-6">
                <nav className="-mb-px flex space-x-8">
                  <button
                    onClick={() => setActiveTab('grid')}
                    className={activeTab === 'grid' ? 'active-tab' : 'inactive-tab'}
                  >
                    Grid View
                  </button>
                  <button
                    onClick={() => setActiveTab('transition')}
                    className={activeTab === 'transition' ? 'active-tab' : 'inactive-tab'}
                  >
                    Phase Transition
                  </button>
                </nav>
              </div>
              
              {/* Tab Content */}
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
      </main>
    </div>
  );
}
```

---

## User Experience Requirements

### Performance
- Show loading indicators during API calls
- Debounce slider changes (don't call API on every move)
- Cache recent results (optional)
- Handle errors gracefully with user-friendly messages

### Responsiveness
- Mobile-friendly (single column on small screens)
- Tablet: Maybe 1.5 column layout
- Desktop: Full two-column layout

### Accessibility
- All inputs have labels
- Proper ARIA attributes
- Keyboard navigation works
- Color contrast meets WCAG AA

### Error Handling
Show friendly error messages for:
- API connection failures
- Invalid parameters (though API validates)
- Timeout on long-running simulations
- Browser compatibility issues

---

## Development Setup

### package.json dependencies
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "recharts": "^2.10.0",
    "lucide-react": "^0.300.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.2.0",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "tailwindcss": "^3.4.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0"
  }
}
```

### Vite Config (vite.config.ts)
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
```

This sets up a dev proxy so you can call `/api/...` instead of `http://localhost:8000/api/...`

### Tailwind Config (tailwind.config.js)
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

---

## Testing the Backend

Before building frontend, verify backend is running:

```bash
# Start backend
cd backend
uvicorn api.main:app --reload

# Or with Docker
docker-compose up -d

# Test endpoints
curl http://localhost:8000/api/health
curl -X POST http://localhost:8000/api/simulate \
  -H "Content-Type: application/json" \
  -d '{"p": 0.6, "N": 50, "num_trials": 100, "algorithm": "cpp"}'
```

Visit `http://localhost:8000/docs` for interactive API documentation.

---

## Implementation Order

1. **Setup Project**
   - Create Vite + React + TypeScript project
   - Install dependencies
   - Setup Tailwind CSS

2. **API Service**
   - Implement `api.ts` with typed functions
   - Test connections to backend

3. **Basic Layout**
   - App shell with header
   - Two-column grid layout
   - Tab navigation

4. **Parameter Controls**
   - Build form with sliders/inputs
   - Validation
   - Submit button with loading state

5. **Simulation Results**
   - Display stats cards
   - Format numbers nicely

6. **Grid Visualization**
   - Fetch and display PNG
   - Show loading state
   - Display stats from header

7. **Phase Transition Plot**
   - Recharts integration
   - Sweep controls
   - Interactive tooltips

8. **Polish**
   - Error handling
   - Loading states
   - Responsive design
   - Accessibility

---

## Design Inspiration

The UI should feel:
- **Scientific but approachable** - Not too technical, clear explanations
- **Clean and modern** - White/light theme, good spacing
- **Interactive** - Responsive controls, live updates
- **Educational** - Tooltips explain concepts

Similar to:
- Desmos calculator (clean, interactive)
- Observable notebooks (scientific but friendly)
- Modern dashboards (Vercel, Netlify UI)

---

## Optional Enhancements (Nice to Have)

1. **Presets** - Quick buttons for interesting p values (0.5, 0.593, 0.7)
2. **Comparison Mode** - Run multiple simulations side-by-side
3. **Export** - Download images/data as CSV
4. **Animation** - Show p gradually increasing with animation
5. **Dark Mode** - Toggle theme
6. **History** - Keep recent simulations
7. **Share** - URL with parameters (query strings)

---

## Notes for Claude Code

- Backend API is complete and tested - don't modify it
- Focus on clean, typed TypeScript code
- Use functional components with hooks
- Tailwind for all styling (no custom CSS unless necessary)
- Error boundaries for graceful failures
- Comments explaining non-obvious logic
- API calls should handle loading/error states
- Keep components reasonably sized (< 200 lines)
- Extract repeated logic into hooks if needed

Good luck! The backend is ready and waiting. 🚀