import { Component, ReactNode } from 'react';
import { AlertCircle } from 'lucide-react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: string | null;
}

export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error, errorInfo: null };
  }

  componentDidCatch(error: Error, errorInfo: any) {
    console.error('Error caught by boundary:', error, errorInfo);
    this.setState({
      error,
      errorInfo: errorInfo.componentStack,
    });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
          <div className="max-w-2xl w-full bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center gap-3 mb-4">
              <AlertCircle className="h-8 w-8 text-red-600" />
              <h1 className="text-2xl font-bold text-gray-900">Something went wrong</h1>
            </div>

            <div className="space-y-4">
              <div>
                <h2 className="font-semibold text-gray-900 mb-2">Error:</h2>
                <pre className="bg-red-50 text-red-800 p-4 rounded-lg overflow-auto text-sm">
                  {this.state.error?.toString()}
                </pre>
              </div>

              {this.state.errorInfo && (
                <div>
                  <h2 className="font-semibold text-gray-900 mb-2">Stack trace:</h2>
                  <pre className="bg-gray-100 text-gray-800 p-4 rounded-lg overflow-auto text-xs max-h-64">
                    {this.state.errorInfo}
                  </pre>
                </div>
              )}

              <button
                onClick={() => window.location.reload()}
                className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                Reload Page
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
