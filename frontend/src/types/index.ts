/**
 * Type definitions for the HomeValuate AI Indian Real Estate Price Prediction application.
 */

export interface FormData {
  area_sqft: string;
  bhk: string;
  bathrooms: string;
  city: string;
  locality: string;
  property_type: string;
  furnishing: string;
}

export type ValidationErrors = Partial<Record<keyof FormData, string>>;

export interface PriceRange {
  lower: number;
  upper: number;
}

export interface ConfidenceInterval {
  lower_bound: number;
  upper_bound: number;
}

export interface ConfidenceMetrics {
  confidence_interval: ConfidenceInterval;
}

export interface PredictionResult {
  predicted_price: number;
  price_range: PriceRange;
  currency: string;
  confidence_metrics?: ConfidenceMetrics;
}

export interface OptionsData {
  cities: string[];
  localities: Record<string, string[]>;
  property_types: string[];
  furnishing_types: string[];
}

export type ErrorType = 'validation' | 'network' | 'server' | 'timeout';

export interface ErrorObject {
  type: ErrorType;
  message: string;
}

export interface BenchmarkItem {
  model: string;
  r2: number;
  mae: number;
  rmse: number;
}

export interface ModelInfoData {
  best_model: string;
  features: string[];
  benchmark: BenchmarkItem[];
  interval_ratios: {
    lower: number;
    upper: number;
  };
  dataset_summary: {
    total_records: number;
    train_records?: number;
    test_records?: number;
    cities_count?: number;
    source?: string;
  };
}
