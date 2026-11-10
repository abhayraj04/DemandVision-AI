import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallbackTitle?: string;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="p-6 rounded-xl bg-slate-900 border border-red-800/60 text-slate-200 font-mono text-xs my-4 space-y-3">
          <div className="flex items-center space-x-2 text-rose-400 font-bold text-sm">
            <AlertTriangle className="w-5 h-5 shrink-0" />
            <span>{this.props.fallbackTitle || 'Module Render Interrupted'}</span>
          </div>
          <p className="text-slate-400 leading-relaxed">
            {this.state.error?.message || 'An unexpected rendering error occurred.'}
          </p>
          <button
            onClick={() => this.setState({ hasError: false, error: null })}
            className="flex items-center space-x-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-cyan-300 rounded border border-slate-700 transition"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Retry Module</span>
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
