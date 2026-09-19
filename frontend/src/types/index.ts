/**
 * Type definitions for the House Price Prediction application.
 */

export interface FormData {
  square_footage: string;
  bedrooms: string;
  bathrooms: string;
  location: string;
  year_built: string;
}

export type ValidationErrors = Partial<Record<keyof FormData, string>>;

export interface ConfidenceInterval {
  lower_bound: number;
  upper_bound: number;
}

export interface ConfidenceMetrics {
  confidence_interval: ConfidenceInterval;
}

export interface PredictionResult {
  predicted_price: number;
  confidence_metrics: ConfidenceMetrics;
}

export type ErrorType = 'validation' | 'network' | 'server' | 'timeout';

export interface ErrorObject {
  type: ErrorType;
  message: string;
}

export interface ModelFeature {
  name: string;
  type: string;
  description: string;
}

export interface ModelMetrics {
  r2_score: number;
  rmse: number;
  unit: string;
}

export interface ModelInfoData {
  model_type: string;
  features: ModelFeature[];
  preprocessing: string[];
  metrics: ModelMetrics;
}
