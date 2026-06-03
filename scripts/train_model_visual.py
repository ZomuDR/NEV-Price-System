import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NEV_Price_System.settings')

import django
django.setup()

import pandas as pd
import numpy as np
from cars.models import Car
from xgboost import XGBRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

FEATURE_COLUMNS = [
    'manufacturer', 'car_class', 'energy_type',
    'motor_power', 'max_horsepower', 'max_speed', 'fuel_tank_volume',
    'curb_weight', 'wheelbase', 'max_torque', 'nedc_fuel_consumption',
    'gear_count', 'width', 'displacement', 'acceleration_time',
    'electric_range', 'front_track', 'seat_count'
]

CATEGORICAL_COLUMNS = ['manufacturer', 'car_class', 'energy_type']

def main():
    print("=" * 60)
    print("  XGBoost Car Price Prediction Model - Training Process")
    print("=" * 60)
    
    cars = Car.objects.all().values()
    df = pd.DataFrame(list(cars))
    print(f"\n[Data Loading] Loaded {len(df)} records from database")
    
    print("\n[Preprocessing] Processing features...")
    feature_df = df[FEATURE_COLUMNS].copy()
    target = df['price'].values
    
    label_encoders = {}
    for col in CATEGORICAL_COLUMNS:
        if col in feature_df.columns:
            le = LabelEncoder()
            feature_df[col] = feature_df[col].fillna('Unknown')
            classes = list(feature_df[col].unique())
            if 'Unknown' not in classes:
                classes.append('Unknown')
            le.fit(classes)
            feature_df[col] = le.transform(feature_df[col].astype(str))
            label_encoders[col] = le
    
    for col in feature_df.columns:
        if col not in CATEGORICAL_COLUMNS:
            feature_df[col] = feature_df[col].fillna(feature_df[col].median())
    
    print(f"[Preprocessing] Feature count: {len(feature_df.columns)}")
    print(f"[Preprocessing] Target range: {target.min():.2f} - {target.max():.2f} (10k CNY)")
    
    X_train, X_test, y_train, y_test = train_test_split(
        feature_df, target, test_size=0.2, random_state=42
    )
    
    print(f"\n[Split] Training samples: {len(X_train)}")
    print(f"[Split] Test samples: {len(X_test)}")
    
    print("\n" + "-" * 60)
    print("  Training Progress")
    print("-" * 60)
    
    model = XGBRegressor(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1,
        eval_metric=['rmse', 'mae']
    )
    
    eval_set = [(X_train, y_train), (X_test, y_test)]
    
    model.fit(
        X_train, y_train,
        eval_set=eval_set,
        verbose=True
    )
    
    print("\n" + "-" * 60)
    print("  Final Evaluation")
    print("-" * 60)
    
    y_pred = model.predict(X_test)
    
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    
    print(f"\n  R2 Score:  {r2:.4f}")
    print(f"  MAE:       {mae:.4f} (10k CNY)")
    print(f"  RMSE:      {rmse:.4f} (10k CNY)")
    
    print("\n" + "=" * 60)
    print("  Training Completed Successfully!")
    print("=" * 60)
    
    results = model.evals_result()
    print("\n[Learning Curve Data]")
    print(f"  Training RMSE (last): {results['validation_0']['rmse'][-1]:.4f}")
    print(f"  Test RMSE (last):     {results['validation_1']['rmse'][-1]:.4f}")
    print(f"  Total boosting rounds: {len(results['validation_0']['rmse'])}")

if __name__ == '__main__':
    main()
