"""
Train a baseline Linear Regression model for house price prediction.
Generates synthetic data and exports a trained model to backend/models/model.pkl.
"""

import os
import pickle
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

def train_and_export_model():
    np.random.seed(42)
    n_samples = 1000

    # Synthetic feature generation within realistic ranges
    square_footage = np.random.uniform(500, 6000, n_samples)
    bedrooms = np.random.randint(1, 7, n_samples)
    bathrooms = np.random.choice([1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0], n_samples)
    location_encoded = np.random.randint(0, 1000, n_samples)
    year_built = np.random.randint(1950, 2024, n_samples)

    # Realistic price formula with Gaussian noise
    price = (
        50000.0
        + square_footage * 240.0
        + bedrooms * 22000.0
        + bathrooms * 18000.0
        + (location_encoded % 100) * 150.0
        + (year_built - 1950) * 1200.0
        + np.random.normal(0, 15000, n_samples)
    )

    X = np.column_stack([square_footage, bedrooms, bathrooms, location_encoded, year_built])
    y = price

    model = LinearRegression()
    model.fit(X, y)

    predictions = model.predict(X)
    rmse = np.sqrt(mean_squared_error(y, predictions))
    r2 = r2_score(y, predictions)

    print(f"Model trained successfully!")
    print(f"R² Score: {r2:.4f}")
    print(f"RMSE: ${rmse:,.2f}")
    print(f"Coefficients: {model.coef_}")
    print(f"Intercept: {model.intercept_:.2f}")

    output_dir = os.path.join(os.path.dirname(__file__), "models")
    os.makedirs(output_dir, exist_ok=True)
    model_path = os.path.join(output_dir, "model.pkl")

    with open(model_path, "wb") as f:
        pickle.dump(model, f)

    print(f"Saved model to: {model_path}")
    return model_path

if __name__ == "__main__":
    train_and_export_model()
