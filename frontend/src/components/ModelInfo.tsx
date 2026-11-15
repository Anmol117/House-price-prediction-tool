import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  BrainCircuit,
  Database,
  Sliders,
  BarChart3,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Award,
} from 'lucide-react';
import { ModelInfoData } from '../types';
import { formatINR } from '../utils/formatting';

const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  import.meta.env.REACT_APP_API_URL ||
  'http://localhost:8000';

const fallbackModelInfo: ModelInfoData = {
  best_model: 'Random Forest',
  features: [
    'area_sqft',
    'bhk',
    'bathrooms',
    'city',
    'locality',
    'property_type',
    'furnishing',
  ],
  benchmark: [
    { model: 'Linear Regression', r2: 0.1502, mae: 4817168.01, rmse: 13049671.28 },
    { model: 'Random Forest', r2: 0.4278, mae: 4752048.42, rmse: 10708244.89 },
    { model: 'Gradient Boosting', r2: 0.3656, mae: 4802673.11, rmse: 11274847.46 },
  ],
  interval_ratios: {
    lower: 0.409,
    upper: 2.861,
  },
  dataset_summary: {
    total_records: 29624,
    train_records: 23699,
    test_records: 5925,
    cities_count: 7,
    source: 'Indian Metropolitan Housing Dataset + Pune residential listings',
  },
};

export const ModelInfo: React.FC = () => {
  const [modelInfo, setModelInfo] = useState<ModelInfoData>(fallbackModelInfo);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchInfo = async () => {
      try {
        const response = await axios.get<ModelInfoData>(`${API_BASE_URL}/model-info`, {
          timeout: 5000,
        });
        if (response.data && response.data.benchmark) {
          setModelInfo(response.data);
        }
      } catch (err) {
        setError('Displaying cached model benchmark metrics.');
      } finally {
        setLoading(false);
      }
    };

    fetchInfo();
  }, []);

  const bestModelData = modelInfo.benchmark.find((b) => b.model === modelInfo.best_model) || modelInfo.benchmark[1];

  return (
    <div className="about-container">
      <div className="about-hero">
        <div className="hero-badge">
          <BrainCircuit size={16} />
          <span>Machine Learning Benchmark</span>
        </div>
        <h1 className="about-title">Model Specifications & Indian Market Performance</h1>
        <p className="about-lead">
          Technical documentation and empirical benchmark comparing regression algorithms trained
          on 29,620+ Indian residential property listings across 7 metropolitan regions.
        </p>
      </div>

      {loading && (
        <div className="info-loading">
          <Loader2 className="spinner" size={32} />
          <span>Loading model documentation...</span>
        </div>
      )}

      {error && (
        <div className="info-notice">
          <AlertCircle size={16} />
          <span>{error}</span>
        </div>
      )}

      {/* Model Overview Cards */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-header">
            <span className="metric-label">Production Model</span>
            <Award size={20} className="text-blue-600" />
          </div>
          <div className="metric-value">{modelInfo.best_model}</div>
          <span className="metric-detail">Ensemble regression with 100 decision trees</span>
        </div>

        <div className="metric-card">
          <div className="metric-header">
            <span className="metric-label">Best Test R² Score</span>
            <BarChart3 size={20} className="text-emerald-600" />
          </div>
          <div className="metric-value">{bestModelData ? (bestModelData.r2 * 100).toFixed(2) : '42.78'}%</div>
          <span className="metric-detail">R² = {bestModelData?.r2.toFixed(4)} on 20% holdout test split</span>
        </div>

        <div className="metric-card">
          <div className="metric-header">
            <span className="metric-label">Mean Absolute Error</span>
            <Sliders size={20} className="text-indigo-600" />
          </div>
          <div className="metric-value">{bestModelData ? formatINR(bestModelData.mae) : '₹47,52,048'}</div>
          <span className="metric-detail">Average absolute deviation in INR</span>
        </div>
      </div>

      {/* Benchmark Comparison Table */}
      <section className="info-section">
        <div className="section-title-group">
          <BarChart3 size={20} className="text-blue-600" />
          <h2 className="section-title">Model Comparison Benchmark (80/20 Test Split)</h2>
        </div>
        <p className="section-desc">
          Evaluated on 5,925 test properties using log-transformed price target to stabilize high price skewness in Indian metropolitan markets:
        </p>

        <div className="features-table-wrapper">
          <table className="features-table">
            <thead>
              <tr>
                <th>Model Architecture</th>
                <th>R² Score</th>
                <th>Mean Absolute Error (MAE)</th>
                <th>Root Mean Squared Error (RMSE)</th>
                <th>Production Status</th>
              </tr>
            </thead>
            <tbody>
              {modelInfo.benchmark.map((item, idx) => {
                const isBest = item.model === modelInfo.best_model;
                return (
                  <tr key={idx} style={isBest ? { backgroundColor: 'rgba(16, 185, 129, 0.08)' } : {}}>
                    <td className="font-semibold text-slate-800">
                      {item.model}
                      {isBest && (
                        <span style={{
                          marginLeft: '8px',
                          padding: '2px 8px',
                          borderRadius: '12px',
                          backgroundColor: '#10b981',
                          color: '#fff',
                          fontSize: '0.75rem',
                          fontWeight: 700
                        }}>
                          Active Best
                        </span>
                      )}
                    </td>
                    <td>
                      <span className="type-tag">{(item.r2 * 100).toFixed(2)}% (R² = {item.r2.toFixed(4)})</span>
                    </td>
                    <td className="text-slate-700 font-medium">{formatINR(item.mae)}</td>
                    <td className="text-slate-700 font-medium">{formatINR(item.rmse)}</td>
                    <td>
                      {isBest ? (
                        <span style={{ color: '#047857', fontWeight: 600 }}>Deploys to /predict</span>
                      ) : (
                        <span style={{ color: '#64748b' }}>Benchmark Baseline</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>

      {/* Features Table */}
      <section className="info-section">
        <div className="section-title-group">
          <Database size={20} className="text-blue-600" />
          <h2 className="section-title">Indian Market Features & Target Variable</h2>
        </div>
        <p className="section-desc">
          Features extracted and normalized across Bengaluru, Chennai, Delhi NCR, Hyderabad, Kolkata, Mumbai, and Pune:
        </p>

        <div className="features-table-wrapper">
          <table className="features-table">
            <thead>
              <tr>
                <th>Feature Name</th>
                <th>Type</th>
                <th>Description & Market Context</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td className="font-semibold text-slate-800">area_sqft</td>
                <td><span className="type-tag">Continuous (Float)</span></td>
                <td className="text-slate-600">Super built-up / carpet area (200 – 20,000 sq ft). Primary size driver.</td>
              </tr>
              <tr>
                <td className="font-semibold text-slate-800">bhk</td>
                <td><span className="type-tag">Integer</span></td>
                <td className="text-slate-600">Bedroom, Hall, Kitchen count (1 – 10). Key layout metric in Indian real estate.</td>
              </tr>
              <tr>
                <td className="font-semibold text-slate-800">bathrooms</td>
                <td><span className="type-tag">Numeric (Step 0.5)</span></td>
                <td className="text-slate-600">Bathroom count (1 – 10). Indicates property tier and convenience.</td>
              </tr>
              <tr>
                <td className="font-semibold text-slate-800">city</td>
                <td><span className="type-tag">Categorical (One-Hot)</span></td>
                <td className="text-slate-600">7 Metro Hubs: Bengaluru, Chennai, Delhi NCR, Hyderabad, Kolkata, Mumbai, Pune.</td>
              </tr>
              <tr>
                <td className="font-semibold text-slate-800">locality</td>
                <td><span className="type-tag">Categorical (One-Hot)</span></td>
                <td className="text-slate-600">Neighborhood / Sector (e.g. Wakad, Whitefield, Andheri West). Rare localities grouped to 'Other'.</td>
              </tr>
              <tr>
                <td className="font-semibold text-slate-800">property_type</td>
                <td><span className="type-tag">Categorical (One-Hot)</span></td>
                <td className="text-slate-600">Apartment, Builder Floor, Independent House, Villa.</td>
              </tr>
              <tr>
                <td className="font-semibold text-slate-800">furnishing</td>
                <td><span className="type-tag">Categorical (One-Hot)</span></td>
                <td className="text-slate-600">Furnished, Semi-furnished, Unfurnished.</td>
              </tr>
              <tr className="target-row">
                <td className="font-semibold text-blue-700">Property Price (Target)</td>
                <td><span className="type-tag tag-target">Continuous (INR ₹)</span></td>
                <td className="text-slate-700 font-medium">Target log-transformed during training (log1p) and expm1-inverted at inference.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      {/* Preprocessing Pipeline */}
      <section className="info-section">
        <div className="section-title-group">
          <Sliders size={20} className="text-teal-600" />
          <h2 className="section-title">Preprocessing & Pipeline Architecture</h2>
        </div>

        <div className="pipeline-steps">
          <div className="pipeline-step">
            <div className="step-number">1</div>
            <div className="step-body">
              <p className="step-text">
                <strong>Data Ingestion & Cleaning:</strong> Aggregation of 34,700+ raw records across 7 metros; removal of PPSF outliers outside 1st–99th percentiles (Rs. 1,244 to Rs. 69,426/sq ft).
              </p>
            </div>
          </div>
          <div className="pipeline-step">
            <div className="step-number">2</div>
            <div className="step-body">
              <p className="step-text">
                <strong>Log Transformation:</strong> Price target transformed via <code>y = log1p(price)</code> to mitigate right-skewness and stabilize residual variance.
              </p>
            </div>
          </div>
          <div className="pipeline-step">
            <div className="step-number">3</div>
            <div className="step-body">
              <p className="step-text">
                <strong>Scikit-learn ColumnTransformer:</strong> OneHotEncoder(handle_unknown='ignore') for city, locality, property_type, and furnishing.
              </p>
            </div>
          </div>
          <div className="pipeline-step">
            <div className="step-number">4</div>
            <div className="step-body">
              <p className="step-text">
                <strong>Empirical Prediction Intervals:</strong> 90% confidence range calculated from the 5th and 95th percentiles of true-to-predicted ratios on the test set.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Trust & Methodology */}
      <section className="info-section trust-section">
        <div className="trust-content">
          <CheckCircle2 size={24} className="text-emerald-600" />
          <div>
            <h3 className="trust-title">Auditable & Production-Ready ML Pipeline</h3>
            <p className="trust-text">
              The model pipeline is serialized using <code>joblib</code> and served via high-throughput FastAPI endpoints, ensuring deterministic predictions and zero data leakage.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};
