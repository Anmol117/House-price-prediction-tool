import React from 'react';
import { DollarSign, TrendingUp, ShieldCheck, Loader2 } from 'lucide-react';
import { PredictionResult as PredictionResultType, ErrorObject } from '../types';
import { formatCurrency } from '../utils/formatting';
import { ErrorDisplay } from './ErrorDisplay';

interface PredictionResultProps {
  prediction: PredictionResultType | null;
  loading: boolean;
  error: ErrorObject | null;
  onRetry?: () => void;
}

export const PredictionResult: React.FC<PredictionResultProps> = ({
  prediction,
  loading,
  error,
  onRetry,
}) => {
  if (loading) {
    return (
      <div className="result-card result-loading" role="status" aria-live="polite">
        <Loader2 className="spinner" size={42} />
        <h3 className="loading-title">Calculating Valuation...</h3>
        <p className="loading-subtitle">
          Our Linear Regression model is analyzing property features and market coefficients.
        </p>
      </div>
    );
  }

  if (error) {
    return <ErrorDisplay error={error} onRetry={onRetry} />;
  }

  if (!prediction) {
    return (
      <div className="result-placeholder">
        <div className="placeholder-icon">
          <DollarSign size={36} />
        </div>
        <h3>Instant Valuation Estimate</h3>
        <p>
          Fill out the property specifications on the left and submit to receive an AI-powered market price prediction and confidence range.
        </p>
      </div>
    );
  }

  const { predicted_price, confidence_metrics } = prediction;
  const { lower_bound, upper_bound } = confidence_metrics.confidence_interval;

  return (
    <div className="result-card result-success" aria-live="polite">
      <div className="result-header">
        <div className="badge badge-success">
          <ShieldCheck size={14} />
          <span>Model Verified</span>
        </div>
        <span className="result-timestamp">Estimate Generated</span>
      </div>

      <div className="price-display-section">
        <span className="price-label">Estimated Market Value</span>
        <div className="price-value">{formatCurrency(predicted_price)}</div>
      </div>

      <div className="confidence-section">
        <div className="confidence-header">
          <TrendingUp size={16} className="text-teal-600" />
          <span className="confidence-title">90% Confidence Interval</span>
        </div>
        <div className="confidence-bounds-grid">
          <div className="bound-box">
            <span className="bound-label">Lower Bound</span>
            <span className="bound-value">{formatCurrency(lower_bound)}</span>
          </div>
          <div className="bound-divider">—</div>
          <div className="bound-box">
            <span className="bound-label">Upper Bound</span>
            <span className="bound-value">{formatCurrency(upper_bound)}</span>
          </div>
        </div>
        <p className="confidence-note">
          Based on historical home sales with comparable square footage, bedrooms, bathrooms, and age.
        </p>
      </div>
    </div>
  );
};
