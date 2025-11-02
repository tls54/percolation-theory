# Percolation Theory - Frontend

Interactive React frontend for the percolation theory simulation API.

## Features

- **Interactive Parameter Controls**: Adjust occupation probability, grid size, number of trials, and algorithm
- **Real-time Simulations**: Run percolation simulations with instant feedback
- **Grid Visualization**: View cluster formations with color-coded visualization
- **Phase Transition Analysis**: Generate and analyze phase transition plots
- **Algorithm Comparison**: Choose between BFS, Numba, and C++ implementations
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`

## Installation

```bash
# Install dependencies
npm install
```

## Development

```bash
# Start development server
npm run dev
```

The app will be available at `http://localhost:3000`

## Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── AlgorithmSelector.tsx    # Algorithm picker (BFS/Numba/C++)
│   │   ├── GridVisualization.tsx    # Cluster grid visualization
│   │   ├── ParameterControls.tsx    # Simulation parameter inputs
│   │   ├── PhaseTransitionPlot.tsx  # Phase transition chart
│   │   └── SimulationResults.tsx    # Results statistics display
│   ├── services/
│   │   └── api.ts                   # API client functions
│   ├── types/
│   │   └── index.ts                 # TypeScript type definitions
│   ├── App.tsx                      # Main app component
│   ├── main.tsx                     # Entry point
│   └── index.css                    # Global styles
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

## Technology Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **Icons**: Lucide React

## API Endpoints Used

- `GET /api/health` - Check backend availability
- `POST /api/simulate` - Run single simulation
- `POST /api/simulate/sweep` - Run parameter sweep for phase transition
- `POST /api/visualize/grid` - Generate cluster visualization

## Usage

1. **Start the backend API** (see backend README)
2. **Run the frontend**: `npm run dev`
3. **Adjust parameters** using the sliders and inputs
4. **Run simulation** to see percolation probability and statistics
5. **View grid visualization** to see cluster formations
6. **Analyze phase transition** by running a parameter sweep

## Features in Detail

### Parameter Controls
- Occupation probability (p): 0.0 - 1.0
- Grid size (N): 10 - 200
- Number of trials: 10 - 500
- Algorithm: BFS, Numba, or C++ (if available)

### Grid Visualization
- Generates PNG image of cluster formation
- Color-coded clusters (largest clusters highlighted)
- Shows spanning clusters
- Downloadable images

### Phase Transition Plot
- Configurable p range and steps
- Sigmoid fit to estimate critical point (p_c)
- Interactive tooltips with exact values
- Displays uncertainty in p_c estimate

## Troubleshooting

**Backend connection errors:**
- Ensure backend is running on `http://localhost:8000`
- Check `/api/health` endpoint is accessible
- Check browser console for CORS errors

**C++ algorithm not available:**
- Check backend has C++ extension compiled
- Falls back to Numba automatically

**Build errors:**
- Clear node_modules: `rm -rf node_modules && npm install`
- Clear Vite cache: `rm -rf .vite`
