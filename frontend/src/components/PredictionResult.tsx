import React from 'react';
import { IndianRupee, TrendingUp, ShieldCheck, Loader2, Info } from 'lucide-react';
import { PredictionResult as PredictionResultType, ErrorObject } from '../types';
import { formatINR, formatLakhCrore } from '../utils/formatting';
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
          Our machine learning pipeline is analyzing area, BHK, city, and locality price trends.
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
          <IndianRupee size={36} />
        </div>
        <h3>Instant Valuation Estimate</h3>
        <p>
          Fill out the property specifications on the left to receive an AI-powered Indian market price prediction and likely price range.
        </p>
      </div>
    );
  }

  const { predicted_price, price_range } = prediction;
  const lower = price_range?.lower ?? (prediction.confidence_metrics?.confidence_interval?.lower_bound || 0);
  const upper = price_range?.upper ?? (prediction.confidence_metrics?.confidence_interval?.upper_bound || 0);

  return (
    <div className="result-card result-success" aria-live="polite">
      <div className="result-header">
        <div className="badge badge-success">
          <ShieldCheck size={14} />
          <span>Model Estimate</span>
        </div>
        <span className="result-timestamp">INR Valuation</span>
      </div>

      <div className="price-display-section">
        <span className="price-label">Estimated Market Price</span>
        <div className="price-value" style={{ fontSize: '2.25rem', fontWeight: 800 }}>
          {formatLakhCrore(predicted_price)}
        </div>
        <div style={{ color: 'var(--color-text-muted)', fontSize: '0.95rem', marginTop: '2px' }}>
          Exact: {formatINR(predicted_price)}
        </div>
      </div>

      <div className="confidence-section">
        <div className="confidence-header">
          <TrendingUp size={16} className="text-teal-600" />
          <span className="confidence-title">Likely Range (90% Interval)</span>
        </div>
        <div className="confidence-bounds-grid">
          <div className="bound-box">
            <span className="bound-label">Lower Bound</span>
            <span className="bound-value" style={{ fontWeight: 700 }}>
              {formatLakhCrore(lower)}
            </span>
            <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
              {formatINR(lower)}
            </span>
          </div>
          <div className="bound-divider">—</div>
          <div className="bound-box">
            <span className="bound-label">Upper Bound</span>
            <span className="bound-value" style={{ fontWeight: 700 }}>
              {formatLakhCrore(upper)}
            </span>
            <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
              {formatINR(upper)}
            </span>
          </div>
        </div>
      </div>

      <div style={{
        marginTop: '1.25rem',
        padding: '0.75rem 1rem',
        backgroundColor: '#f8fafc',
        borderRadius: '8px',
        border: '1px solid #e2e8f0',
        display: 'flex',
        alignItems: 'flex-start',
        gap: '0.5rem',
        fontSize: '0.8125rem',
        color: '#475569',
        lineHeight: 1.4
      }}>
        <Info size={16} style={{ flexShrink: 0, marginTop: '2px', color: '#64748b' }} />
        <span>
          <strong>Disclaimer:</strong> Estimate based on listing prices, not a valuation or registered sale price.
        </span>
      </div>
    </div>
  );
};
