import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Maximize2,
  Bed,
  Bath,
  MapPin,
  Building,
  Armchair,
  Sparkles,
  RotateCcw,
} from 'lucide-react';
import {
  FormData,
  ValidationErrors,
  PredictionResult as PredictionResultType,
  ErrorObject,
  OptionsData
} from '../types';
import { validateField, validateForm } from '../utils/validation';
import { PredictionResult } from './PredictionResult';

const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  import.meta.env.REACT_APP_API_URL ||
  'http://localhost:8000';

const initialFormData: FormData = {
  area_sqft: '',
  bhk: '',
  bathrooms: '',
  city: '',
  locality: '',
  property_type: 'Apartment',
  furnishing: 'Semi-furnished',
};

const defaultOptions: OptionsData = {
  cities: ['Bengaluru', 'Chennai', 'Delhi NCR', 'Hyderabad', 'Kolkata', 'Mumbai', 'Pune'],
  localities: {
    'Pune': ['Wakad', 'Baner', 'Hinjewadi', 'Kothrud', 'Viman Nagar', 'Kalyani Nagar', 'Other'],
    'Bengaluru': ['Whitefield', 'Electronic City', 'Indiranagar', 'HSR Layout', 'Koramangala', 'Other'],
    'Mumbai': ['Andheri West', 'Bandra West', 'Thane West', 'Kandivali East', 'Powai', 'Other'],
    'Delhi NCR': ['Sector 62 Noida', 'Dwarka', 'Sector 57 Gurgaon', 'Rohini', 'Other'],
    'Hyderabad': ['Gachibowli', 'Hitech City', 'Madhapur', 'Kondapur', 'Other'],
    'Chennai': ['Velachery', 'OMR', 'Anna Nagar', 'Adyar', 'Other'],
    'Kolkata': ['New Town', 'Rajarhat', 'Salt Lake', 'Ballygunge', 'Other'],
  },
  property_types: ['Apartment', 'Builder Floor', 'Independent House', 'Villa'],
  furnishing_types: ['Furnished', 'Semi-furnished', 'Unfurnished'],
};

export const PredictionForm: React.FC = () => {
  const [formData, setFormData] = useState<FormData>(initialFormData);
  const [options, setOptions] = useState<OptionsData>(defaultOptions);
  const [errors, setErrors] = useState<ValidationErrors>({});
  const [touched, setTouched] = useState<Record<keyof FormData, boolean>>({
    area_sqft: false,
    bhk: false,
    bathrooms: false,
    city: false,
    locality: false,
    property_type: false,
    furnishing: false,
  });
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [prediction, setPrediction] = useState<PredictionResultType | null>(null);
  const [error, setError] = useState<ErrorObject | null>(null);

  // Fetch dynamic metadata options from backend
  useEffect(() => {
    const fetchOptions = async () => {
      try {
        const res = await axios.get<OptionsData>(`${API_BASE_URL}/options`, { timeout: 5000 });
        if (res.data && res.data.cities && res.data.cities.length > 0) {
          setOptions(res.data);
        }
      } catch (err) {
        // Fallback options will remain in place
      }
    };
    fetchOptions();
  }, []);

  const { isValid } = validateForm(formData);

  const handleInputChange = (field: keyof FormData, value: string) => {
    let updatedForm = { ...formData, [field]: value };

    // Cascading City -> Locality reset if changed
    if (field === 'city') {
      const cityLocalities = options.localities[value] || [];
      if (!cityLocalities.includes(formData.locality)) {
        updatedForm.locality = cityLocalities[0] || '';
      }
    }

    setFormData(updatedForm);

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

    setTouched({
      area_sqft: true,
      bhk: true,
      bathrooms: true,
      city: true,
      locality: true,
      property_type: true,
      furnishing: true,
    });

    const validation = validateForm(formData);
    setErrors(validation.errors);

    if (!validation.isValid) {
      return;
    }

    setError(null);
    setPrediction(null);
    setIsSubmitting(true);

    try {
      const payload = {
        area_sqft: parseFloat(formData.area_sqft),
        bhk: parseInt(formData.bhk, 10),
        bathrooms: parseFloat(formData.bathrooms),
        city: formData.city.trim(),
        locality: formData.locality.trim(),
        property_type: formData.property_type.trim(),
        furnishing: formData.furnishing.trim(),
      };

      const response = await axios.post<PredictionResultType>(
        `${API_BASE_URL}/predict`,
        payload,
        {
          timeout: 30000,
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
      area_sqft: false,
      bhk: false,
      bathrooms: false,
      city: false,
      locality: false,
      property_type: false,
      furnishing: false,
    });
    setPrediction(null);
    setError(null);
  };

  const loadSampleData = () => {
    setFormData({
      area_sqft: '1150',
      bhk: '2',
      bathrooms: '2',
      city: 'Pune',
      locality: 'Wakad',
      property_type: 'Apartment',
      furnishing: 'Semi-furnished',
    });
    setErrors({});
    setError(null);
  };

  // Localities for the selected city
  const currentLocalities = formData.city
    ? options.localities[formData.city] || ['Other']
    : [];

  return (
    <div className="predictor-container">
      <div className="predictor-grid">
        {/* Form Card */}
        <section className="form-card">
          <div className="form-header">
            <div>
              <h2 className="form-title">Property Details</h2>
              <p className="form-subtitle">Enter Indian residential property specs for AI market valuation</p>
            </div>
            <button
              type="button"
              onClick={loadSampleData}
              className="btn-link"
              title="Fill form with sample Pune (Wakad) property"
            >
              Fill Sample (Pune)
            </button>
          </div>

          <form onSubmit={handleSubmit} noValidate className="property-form">
            {/* Area in Sq Ft */}
            <div className="form-group">
              <label htmlFor="area_sqft" className="form-label">
                <Maximize2 size={16} />
                <span>Super Built-up / Carpet Area</span>
                <span className="required-star">*</span>
              </label>
              <div className="input-wrapper">
                <input
                  id="area_sqft"
                  type="number"
                  name="area_sqft"
                  value={formData.area_sqft}
                  onChange={(e) => handleInputChange('area_sqft', e.target.value)}
                  onBlur={() => handleBlur('area_sqft')}
                  placeholder="e.g. 1150"
                  min="200"
                  max="20000"
                  className={`form-input ${errors.area_sqft ? 'input-error' : ''}`}
                  disabled={isSubmitting}
                />
                <span className="input-unit">sq ft</span>
              </div>
              {errors.area_sqft && (
                <p className="field-error" role="alert">{errors.area_sqft}</p>
              )}
            </div>

            {/* BHK & Bathrooms Row */}
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="bhk" className="form-label">
                  <Bed size={16} />
                  <span>BHK / Bedrooms</span>
                  <span className="required-star">*</span>
                </label>
                <input
                  id="bhk"
                  type="number"
                  name="bhk"
                  value={formData.bhk}
                  onChange={(e) => handleInputChange('bhk', e.target.value)}
                  onBlur={() => handleBlur('bhk')}
                  placeholder="e.g. 2"
                  min="1"
                  max="10"
                  step="1"
                  className={`form-input ${errors.bhk ? 'input-error' : ''}`}
                  disabled={isSubmitting}
                />
                {errors.bhk && (
                  <p className="field-error" role="alert">{errors.bhk}</p>
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
                  placeholder="e.g. 2"
                  min="1"
                  max="10"
                  step="0.5"
                  className={`form-input ${errors.bathrooms ? 'input-error' : ''}`}
                  disabled={isSubmitting}
                />
                {errors.bathrooms && (
                  <p className="field-error" role="alert">{errors.bathrooms}</p>
                )}
              </div>
            </div>

            {/* City & Locality Cascading Row */}
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="city" className="form-label">
                  <MapPin size={16} />
                  <span>City</span>
                  <span className="required-star">*</span>
                </label>
                <select
                  id="city"
                  name="city"
                  value={formData.city}
                  onChange={(e) => handleInputChange('city', e.target.value)}
                  onBlur={() => handleBlur('city')}
                  className={`form-input ${errors.city ? 'input-error' : ''}`}
                  disabled={isSubmitting}
                >
                  <option value="">Select Indian City</option>
                  {options.cities.map((c) => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
                {errors.city && (
                  <p className="field-error" role="alert">{errors.city}</p>
                )}
              </div>

              <div className="form-group">
                <label htmlFor="locality" className="form-label">
                  <MapPin size={16} />
                  <span>Locality / Sector</span>
                  <span className="required-star">*</span>
                </label>
                {currentLocalities.length > 0 ? (
                  <select
                    id="locality"
                    name="locality"
                    value={formData.locality}
                    onChange={(e) => handleInputChange('locality', e.target.value)}
                    onBlur={() => handleBlur('locality')}
                    className={`form-input ${errors.locality ? 'input-error' : ''}`}
                    disabled={isSubmitting || !formData.city}
                  >
                    <option value="">Select Locality</option>
                    {currentLocalities.map((loc) => (
                      <option key={loc} value={loc}>{loc}</option>
                    ))}
                  </select>
                ) : (
                  <input
                    id="locality"
                    type="text"
                    name="locality"
                    value={formData.locality}
                    onChange={(e) => handleInputChange('locality', e.target.value)}
                    onBlur={() => handleBlur('locality')}
                    placeholder="e.g. Wakad"
                    maxLength={100}
                    className={`form-input ${errors.locality ? 'input-error' : ''}`}
                    disabled={isSubmitting}
                  />
                )}
                {errors.locality && (
                  <p className="field-error" role="alert">{errors.locality}</p>
                )}
              </div>
            </div>

            {/* Property Type & Furnishing Row */}
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="property_type" className="form-label">
                  <Building size={16} />
                  <span>Property Type</span>
                  <span className="required-star">*</span>
                </label>
                <select
                  id="property_type"
                  name="property_type"
                  value={formData.property_type}
                  onChange={(e) => handleInputChange('property_type', e.target.value)}
                  onBlur={() => handleBlur('property_type')}
                  className={`form-input ${errors.property_type ? 'input-error' : ''}`}
                  disabled={isSubmitting}
                >
                  {options.property_types.map((t) => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </select>
                {errors.property_type && (
                  <p className="field-error" role="alert">{errors.property_type}</p>
                )}
              </div>

              <div className="form-group">
                <label htmlFor="furnishing" className="form-label">
                  <Armchair size={16} />
                  <span>Furnishing Status</span>
                  <span className="required-star">*</span>
                </label>
                <select
                  id="furnishing"
                  name="furnishing"
                  value={formData.furnishing}
                  onChange={(e) => handleInputChange('furnishing', e.target.value)}
                  onBlur={() => handleBlur('furnishing')}
                  className={`form-input ${errors.furnishing ? 'input-error' : ''}`}
                  disabled={isSubmitting}
                >
                  {options.furnishing_types.map((f) => (
                    <option key={f} value={f}>{f}</option>
                  ))}
                </select>
                {errors.furnishing && (
                  <p className="field-error" role="alert">{errors.furnishing}</p>
                )}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="form-actions">
              <button
                type="submit"
                disabled={!isValid || isSubmitting}
                className="btn-primary"
              >
                <Sparkles size={18} />
                <span>{isSubmitting ? 'Predicting...' : 'Predict Property Price (₹)'}</span>
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
