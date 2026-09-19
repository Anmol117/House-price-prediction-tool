import React, { useState } from 'react';
import axios from 'axios';
import {
  Maximize2,
  Bed,
  Bath,
  MapPin,
  Calendar,
  Sparkles,
  RotateCcw,
} from 'lucide-react';
import { FormData, ValidationErrors, PredictionResult as PredictionResultType, ErrorObject } from '../types';
import { validateField, validateForm } from '../utils/validation';
import { PredictionResult } from './PredictionResult';

const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  import.meta.env.REACT_APP_API_URL ||
  'http://localhost:8000';

const initialFormData: FormData = {
  square_footage: '',
  bedrooms: '',
  bathrooms: '',
  location: '',
  year_built: '',
};

export const PredictionForm: React.FC = () => {
  const [formData, setFormData] = useState<FormData>(initialFormData);
  const [errors, setErrors] = useState<ValidationErrors>({});
  const [touched, setTouched] = useState<Record<keyof FormData, boolean>>({
    square_footage: false,
    bedrooms: false,
    bathrooms: false,
    location: false,
    year_built: false,
  });
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [prediction, setPrediction] = useState<PredictionResultType | null>(null);
  const [error, setError] = useState<ErrorObject | null>(null);

  // Check overall form validity
  const { isValid } = validateForm(formData);

  const handleInputChange = (field: keyof FormData, value: string) => {
    const updatedForm = { ...formData, [field]: value };
    setFormData(updatedForm);

    // Validate if field has been touched
    if (touched[field]) {
      const fieldError = validateField(field, value);
      setErrors((prev) => ({
        ...prev,
        [field]: fieldError || undefined,
      }));
    }
  };

  const handleBlur = (field: keyof FormData) => {
    setTouched((prev) => ({ ...prev, [field]: true }));
    const fieldError = validateField(field, formData[field]);
    setErrors((prev) => ({
      ...prev,
      [field]: fieldError || undefined,
    }));
  };

  const handleSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();

    // Mark all as touched
    setTouched({
      square_footage: true,
      bedrooms: true,
      bathrooms: true,
      location: true,
      year_built: true,
    });

    const validation = validateForm(formData);
    setErrors(validation.errors);

    if (!validation.isValid) {
      return;
    }

    // Clear previous errors and results before new request
    setError(null);
    setPrediction(null);
    setIsSubmitting(true);

    try {
      const payload = {
        square_footage: parseFloat(formData.square_footage),
        bedrooms: parseInt(formData.bedrooms, 10),
        bathrooms: parseFloat(formData.bathrooms),
        location: formData.location.trim(),
        year_built: parseInt(formData.year_built, 10),
      };

      const response = await axios.post<PredictionResultType>(
        `${API_BASE_URL}/predict`,
        payload,
        {
          timeout: 30000, // 30-second timeout
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      setPrediction(response.data);
    } catch (err: any) {
      if (axios.isAxiosError(err)) {
        if (err.code === 'ECONNABORTED' || err.message?.includes('timeout')) {
          setError({
            type: 'timeout',
            message: 'Prediction request timed out after 30 seconds. Please check backend connection and retry.',
          });
        } else if (!err.response) {
          setError({
            type: 'network',
            message: 'Network error: Unable to connect to prediction service. Please ensure the backend server is running.',
          });
        } else if (err.response.status === 400) {
          const errorMsg =
            err.response.data?.error ||
            err.response.data?.detail ||
            'Invalid property details submitted. Please check the form values.';
          setError({
            type: 'validation',
            message: errorMsg,
          });
        } else if (err.response.status === 413) {
          setError({
            type: 'server',
            message: 'Request payload too large (exceeds 1 MB limit).',
          });
        } else if (err.response.status === 503) {
          setError({
            type: 'server',
            message: 'Prediction service unavailable: Machine learning model is not loaded.',
          });
        } else {
          const errorMsg = err.response.data?.error || 'Prediction service error encountered.';
          setError({
            type: 'server',
            message: errorMsg,
          });
        }
      } else {
        setError({
          type: 'server',
          message: err.message || 'An unexpected error occurred while predicting house price.',
        });
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReset = () => {
    setFormData(initialFormData);
    setErrors({});
    setTouched({
      square_footage: false,
      bedrooms: false,
      bathrooms: false,
      location: false,
      year_built: false,
    });
    setPrediction(null);
    setError(null);
  };

  const loadSampleData = () => {
    setFormData({
      square_footage: '2450',
      bedrooms: '4',
      bathrooms: '2.5',
      location: 'Austin, TX',
      year_built: '2016',
    });
    setErrors({});
    setError(null);
  };

  return (
    <div className="predictor-container">
      <div className="predictor-grid">
        {/* Form Card */}
        <section className="form-card">
          <div className="form-header">
            <div>
              <h2 className="form-title">Property Details</h2>
              <p className="form-subtitle">Enter property specs to calculate market valuation</p>
            </div>
            <button
              type="button"
              onClick={loadSampleData}
              className="btn-link"
              title="Fill form with sample data"
            >
              Fill Sample
            </button>
          </div>

          <form onSubmit={handleSubmit} noValidate className="property-form">
            {/* Square Footage */}
            <div className="form-group">
              <label htmlFor="square_footage" className="form-label">
                <Maximize2 size={16} />
                <span>Square Footage</span>
                <span className="required-star">*</span>
              </label>
              <div className="input-wrapper">
                <input
                  id="square_footage"
                  type="number"
                  name="square_footage"
                  value={formData.square_footage}
                  onChange={(e) => handleInputChange('square_footage', e.target.value)}
                  onBlur={() => handleBlur('square_footage')}
                  placeholder="e.g. 2400"
                  min="1"
                  max="100000"
                  className={`form-input ${errors.square_footage ? 'input-error' : ''}`}
                  disabled={isSubmitting}
                />
                <span className="input-unit">sq ft</span>
              </div>
              {errors.square_footage && (
                <p className="field-error" role="alert">{errors.square_footage}</p>
              )}
            </div>

            {/* Bedrooms & Bathrooms Row */}
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="bedrooms" className="form-label">
                  <Bed size={16} />
                  <span>Bedrooms</span>
                  <span className="required-star">*</span>
                </label>
                <input
                  id="bedrooms"
                  type="number"
                  name="bedrooms"
                  value={formData.bedrooms}
                  onChange={(e) => handleInputChange('bedrooms', e.target.value)}
                  onBlur={() => handleBlur('bedrooms')}
                  placeholder="e.g. 3"
                  min="0"
                  max="20"
                  step="1"
                  className={`form-input ${errors.bedrooms ? 'input-error' : ''}`}
                  disabled={isSubmitting}
                />
                {errors.bedrooms && (
                  <p className="field-error" role="alert">{errors.bedrooms}</p>
                )}
              </div>

              <div className="form-group">
                <label htmlFor="bathrooms" className="form-label">
                  <Bath size={16} />
                  <span>Bathrooms</span>
                  <span className="required-star">*</span>
                </label>
                <input
                  id="bathrooms"
                  type="number"
                  name="bathrooms"
                  value={formData.bathrooms}
                  onChange={(e) => handleInputChange('bathrooms', e.target.value)}
                  onBlur={() => handleBlur('bathrooms')}
                  placeholder="e.g. 2.5"
                  min="0"
                  max="20"
                  step="0.5"
                  className={`form-input ${errors.bathrooms ? 'input-error' : ''}`}
                  disabled={isSubmitting}
                />
                {errors.bathrooms && (
                  <p className="field-error" role="alert">{errors.bathrooms}</p>
                )}
              </div>
            </div>

            {/* Location */}
            <div className="form-group">
              <label htmlFor="location" className="form-label">
                <MapPin size={16} />
                <span>Location (City, State / Neighborhood)</span>
                <span className="required-star">*</span>
              </label>
              <input
                id="location"
                type="text"
                name="location"
                value={formData.location}
                onChange={(e) => handleInputChange('location', e.target.value)}
                onBlur={() => handleBlur('location')}
                placeholder="e.g. San Francisco, CA"
                maxLength={200}
                className={`form-input ${errors.location ? 'input-error' : ''}`}
                disabled={isSubmitting}
              />
              {errors.location && (
                <p className="field-error" role="alert">{errors.location}</p>
              )}
            </div>

            {/* Year Built */}
            <div className="form-group">
              <label htmlFor="year_built" className="form-label">
                <Calendar size={16} />
                <span>Year Built</span>
                <span className="required-star">*</span>
              </label>
              <input
                id="year_built"
                type="number"
                name="year_built"
                value={formData.year_built}
                onChange={(e) => handleInputChange('year_built', e.target.value)}
                onBlur={() => handleBlur('year_built')}
                placeholder="e.g. 2015"
                min="1800"
                max={new Date().getFullYear() + 1}
                className={`form-input ${errors.year_built ? 'input-error' : ''}`}
                disabled={isSubmitting}
              />
              {errors.year_built && (
                <p className="field-error" role="alert">{errors.year_built}</p>
              )}
            </div>

            {/* Action Buttons */}
            <div className="form-actions">
              <button
                type="submit"
                disabled={!isValid || isSubmitting}
                className="btn-primary"
              >
                <Sparkles size={18} />
                <span>{isSubmitting ? 'Predicting...' : 'Predict House Price'}</span>
              </button>

              <button
                type="button"
                onClick={handleReset}
                disabled={isSubmitting}
                className="btn-secondary"
              >
                <RotateCcw size={16} />
                <span>Reset</span>
              </button>
            </div>
          </form>
        </section>

        {/* Prediction Results Card */}
        <section className="results-container">
          <PredictionResult
            prediction={prediction}
            loading={isSubmitting}
            error={error}
            onRetry={() => handleSubmit()}
          />
        </section>
      </div>
    </div>
  );
};
