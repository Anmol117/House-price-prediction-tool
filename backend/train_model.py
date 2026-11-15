"""
Train Indian Metropolitan Housing Price Prediction Models.
Compares Linear Regression, Random Forest, and Gradient Boosting on an 80/20 split.
Saves the best model pipeline to models/model.joblib and metadata/metrics to models/model_meta.json.
"""

import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


def train_and_benchmark():
    base_dir = os.path.dirname(__file__)
    data_path = os.path.join(base_dir, 'data', 'india_housing.csv')
    models_dir = os.path.join(base_dir, 'models')
    os.makedirs(models_dir, exist_ok=True)

    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Dataset not found at {data_path}. Run prepare_dataset.py first.")

    print(f"Loading dataset from {data_path}...")
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} rows.")

    # Target: Log-transformed price to stabilize variance
    y = np.log1p(df['price'].values)
    feature_cols = ['area_sqft', 'bhk', 'bathrooms', 'city', 'locality', 'property_type', 'furnishing']
    X = df[feature_cols].copy()

    # Preprocessor pipeline
    categorical_features = ['city', 'locality', 'property_type', 'furnishing']
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features)
        ],
        remainder='passthrough'
    )

    # 80/20 train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )
    print(f"Training on {len(X_train)} samples, testing on {len(X_test)} samples.")

    models = {
        'Linear Regression': LinearRegression(),
        'Random Forest': RandomForestRegressor(n_estimators=100, max_depth=20, random_state=42, n_jobs=-1),
        'Gradient Boosting': GradientBoostingRegressor(n_estimators=120, max_depth=6, random_state=42)
    }

    results = []
    trained_pipelines = {}
    best_name = None
    best_r2 = -float('inf')

    # Original scale test targets for realistic error metrics (INR)
    y_test_original = np.expm1(y_test)

    for name, regressor in models.items():
        print(f"\n--- Training {name} ---")
        pipe = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('regressor', regressor)
        ])

        pipe.fit(X_train, y_train)
        trained_pipelines[name] = pipe

        # Predictions on test set (converted back to INR)
        y_pred_log = pipe.predict(X_test)
        y_pred = np.expm1(y_pred_log)

        # Handle any negative predictions safely
        y_pred = np.clip(y_pred, a_min=100000.0, a_max=None)

        r2 = float(r2_score(y_test_original, y_pred))
        mae = float(mean_absolute_error(y_test_original, y_pred))
        rmse = float(np.sqrt(mean_squared_error(y_test_original, y_pred)))

        print(f"{name} Results:")
        print(f"  R² Score: {r2:.4f}")
        print(f"  MAE:      Rs.{mae:,.2f}")
        print(f"  RMSE:     Rs.{rmse:,.2f}")

        results.append({
            'model': name,
            'r2': round(r2, 4),
            'mae': round(mae, 2),
            'rmse': round(rmse, 2)
        })

        if r2 > best_r2:
            best_r2 = r2
            best_name = name

    print(f"\nBest Model: {best_name} with R² = {best_r2:.4f}")
    best_pipe = trained_pipelines[best_name]

    # Compute empirical prediction interval ratios on test set
    best_pred_log = best_pipe.predict(X_test)
    best_pred = np.expm1(best_pred_log)
    best_pred = np.clip(best_pred, a_min=100000.0, a_max=None)

    error_ratios = y_test_original / best_pred
    # 5th and 95th percentiles of true / predicted ratio
    low_ratio = float(np.percentile(error_ratios, 5))
    high_ratio = float(np.percentile(error_ratios, 95))
    print(f"Empirical 90% Prediction Interval: [{low_ratio:.3f}x, {high_ratio:.3f}x]")

    # Build unique option mappings
    cities = sorted(df['city'].dropna().unique().tolist())
    localities_by_city = {}
    for city in cities:
        city_locs = sorted(df[df['city'] == city]['locality'].dropna().unique().tolist())
        # Ensure 'Other' is at the end or included
        if 'Other' in city_locs:
            city_locs.remove('Other')
            city_locs.append('Other')
        localities_by_city[city] = city_locs

    property_types = sorted(df['property_type'].dropna().unique().tolist())
    furnishing_types = ['Furnished', 'Semi-furnished', 'Unfurnished']

    meta = {
        'best_model': best_name,
        'features': feature_cols,
        'benchmark': results,
        'interval_ratios': {
            'lower': round(low_ratio, 3),
            'upper': round(high_ratio, 3)
        },
        'cities': cities,
        'localities': localities_by_city,
        'property_types': property_types,
        'furnishing_types': furnishing_types,
        'dataset_summary': {
            'total_records': len(df),
            'train_records': len(X_train),
            'test_records': len(X_test),
            'cities_count': len(cities),
            'source': 'Indian Metropolitan Housing Dataset (Kaggle/GitHub) + Pune residential listings'
        }
    }

    # Save artifacts
    model_joblib_path = os.path.join(models_dir, 'model.joblib')
    joblib.dump(best_pipe, model_joblib_path)
    print(f"Saved best model pipeline to: {model_joblib_path}")

    meta_path = os.path.join(models_dir, 'model_meta.json')
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    print(f"Saved metadata to: {meta_path}")

    return model_joblib_path, meta_path


if __name__ == '__main__':
    train_and_benchmark()
