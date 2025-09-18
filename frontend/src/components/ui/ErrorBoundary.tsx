import React, { Component, ErrorInfo, ReactNode } from 'react';
import { ExclamationTriangleIcon, ArrowPathIcon } from '@heroicons/react/24/outline';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
  errorInfo?: ErrorInfo;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    this.setState({
      error,
      errorInfo,
    });
  }

  private handleReload = () => {
    window.location.reload();
  };

  private handleReset = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined });
  };

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 px-4">
          <div className="max-w-md w-full bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 text-center">
            {/* Error Icon */}
            <div className="w-16 h-16 bg-red-100 dark:bg-red-900/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <ExclamationTriangleIcon className="w-8 h-8 text-red-600 dark:text-red-400" />
            </div>

            {/* Error Title */}
            <h1 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              حدث خطأ غير متوقع
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              نعتذر، حدث خطأ في تحميل الصفحة. يرجى المحاولة مرة أخرى.
            </p>

            {/* Error Details (Development only) */}
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details className="text-left bg-gray-100 dark:bg-gray-700 rounded p-3 mb-4 text-sm">
                <summary className="cursor-pointer font-medium text-gray-700 dark:text-gray-300 mb-2">
                  تفاصيل الخطأ
                </summary>
                <pre className="text-red-600 dark:text-red-400 whitespace-pre-wrap">
                  {this.state.error.message}
                  {this.state.errorInfo?.componentStack}
                </pre>
              </details>
            )}

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-3">
              <button
                onClick={this.handleReset}
                className="flex-1 btn btn-outline"
              >
                <ArrowPathIcon className="w-4 h-4 mr-2" />
                المحاولة مرة أخرى
              </button>
              <button
                onClick={this.handleReload}
                className="flex-1 btn btn-primary"
              >
                إعادة تحميل الصفحة
              </button>
            </div>

            {/* Contact Support */}
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-4">
              إذا استمر المشكلة، يرجى التواصل مع{' '}
              <a href="mailto:support@finclick.ai" className="text-primary-600 hover:text-primary-700">
                الدعم الفني
              </a>
            </p>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;