import React from 'react';
import { AlertCircle, WifiOff, Clock, Server, RefreshCw } from 'lucide-react';
import { ErrorObject } from '../types';

interface ErrorDisplayProps {
  error: ErrorObject;
  onRetry?: () => void;
}

export const ErrorDisplay: React.FC<ErrorDisplayProps> = ({ error, onRetry }) => {
  const getIcon = () => {
    switch (error.type) {
      case 'network':
        return <WifiOff className="error-icon text-amber-500" size={24} />;
      case 'timeout':
        return <Clock className="error-icon text-amber-500" size={24} />;
      case 'server':
        return <Server className="error-icon text-red-500" size={24} />;
      case 'validation':
      default:
        return <AlertCircle className="error-icon text-red-500" size={24} />;
    }
  };

  const getLabel = () => {
    switch (error.type) {
      case 'network':
        return 'Network Error';
      case 'timeout':
        return 'Request Timed Out';
      case 'server':
        return 'Server Error';
      case 'validation':
        return 'Validation Error';
      default:
        return 'Error';
    }
  };

  return (
    <div className={`error-card error-${error.type}`} role="alert">
      <div className="error-content">
        <div className="error-icon-wrapper">{getIcon()}</div>
        <div className="error-text-wrapper">
          <span className="error-badge">{getLabel()}</span>
          <p className="error-message">{error.message}</p>
        </div>
      </div>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="btn-retry"
          aria-label="Retry request"
        >
          <RefreshCw size={16} />
          <span>Retry</span>
        </button>
      )}
    </div>
  );
};
