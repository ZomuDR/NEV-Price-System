import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NEV_Price_System.settings')

import django
django.setup()

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from cars.models import Car, MLModel
from xgboost import XGBRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

try:
    import shap
except ImportError:
    print("SHAP not installed. Installing...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'shap'])
    import shap

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
    print("  Model Analysis: Convergence & Residuals & SHAP")
    print("=" * 60)
    
    cars = Car.objects.all().values()
    df = pd.DataFrame(list(cars))
    print(f"\n[Data] Loaded {len(df)} records")
    
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
    
    X_train, X_test, y_train, y_test = train_test_split(
        feature_df, target, test_size=0.2, random_state=42
    )
    
    print(f"[Split] Training: {len(X_train)}, Validation: {len(X_test)}")
    
    print("\n[Training] Training model with evaluation...")
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
    model.fit(X_train, y_train, eval_set=eval_set, verbose=False)
    print("[Training] Model trained successfully")
    
    results = model.evals_result()
    
    y_pred = model.predict(X_test)
    residuals = y_test - y_pred
    
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    
    print(f"\n[Metrics] R2: {r2:.4f}, MAE: {mae:.4f}, RMSE: {rmse:.4f}")
    
    print("\n[SHAP] Computing SHAP values...")
    explainer = shap.TreeExplainer(model)
    X_sample = X_test.iloc[:100] if len(X_test) > 100 else X_test
    shap_values = explainer.shap_values(X_sample)
    
    fig = plt.figure(figsize=(18, 16))
    fig.suptitle('Model Analysis: Convergence, Residuals & SHAP', fontsize=18, fontweight='bold', y=1.02)
    
    print("\n[Plot 1] Learning Curve (Training vs Validation)...")
    ax1 = plt.subplot(2, 3, 1)
    epochs = len(results['validation_0']['rmse'])
    x_axis = range(0, epochs)
    
    ax1.plot(x_axis, results['validation_0']['rmse'], 'b-', label='Training Set', linewidth=2)
    ax1.plot(x_axis, results['validation_1']['rmse'], 'r-', label='Validation Set', linewidth=2)
    ax1.set_xlabel('Boosting Rounds', fontsize=10)
    ax1.set_ylabel('RMSE (10k CNY)', fontsize=10)
    ax1.set_title('Learning Curve - RMSE', fontsize=12, fontweight='bold')
    ax1.legend(loc='upper right', fontsize=9)
    ax1.grid(True, alpha=0.3)
    
    min_val_rmse = min(results['validation_1']['rmse'])
    min_val_epoch = results['validation_1']['rmse'].index(min_val_rmse)
    ax1.axhline(y=min_val_rmse, color='g', linestyle='--', alpha=0.5)
    ax1.annotate(f'Best: {min_val_rmse:.2f}', xy=(min_val_epoch, min_val_rmse), 
                 xytext=(min_val_epoch+10, min_val_rmse+5), fontsize=8,
                 arrowprops=dict(arrowstyle='->', color='green'))
    
    print("[Plot 2] Learning Curve (MAE)...")
    ax2 = plt.subplot(2, 3, 2)
    ax2.plot(x_axis, results['validation_0']['mae'], 'b-', label='Training Set', linewidth=2)
    ax2.plot(x_axis, results['validation_1']['mae'], 'r-', label='Validation Set', linewidth=2)
    ax2.set_xlabel('Boosting Rounds', fontsize=10)
    ax2.set_ylabel('MAE (10k CNY)', fontsize=10)
    ax2.set_title('Learning Curve - MAE', fontsize=12, fontweight='bold')
    ax2.legend(loc='upper right', fontsize=9)
    ax2.grid(True, alpha=0.3)
    
    print("[Plot 3] Residual Distribution...")
    ax3 = plt.subplot(2, 3, 3)
    n, bins, patches = ax3.hist(residuals, bins=50, color='steelblue', edgecolor='white', alpha=0.7, density=True)
    
    from scipy import stats
    kde_x = np.linspace(residuals.min(), residuals.max(), 100)
    kde = stats.gaussian_kde(residuals)
    ax3.plot(kde_x, kde(kde_x), 'r-', linewidth=2, label='KDE')
    
    ax3.axvline(x=0, color='green', linestyle='--', linewidth=2, label='Zero Residual')
    ax3.axvline(x=residuals.mean(), color='orange', linestyle='-', linewidth=2, label=f'Mean: {residuals.mean():.2f}')
    
    ax3.set_xlabel('Residual (Actual - Predicted)', fontsize=10)
    ax3.set_ylabel('Density', fontsize=10)
    ax3.set_title('Residual Distribution', fontsize=12, fontweight='bold')
    ax3.legend(loc='upper right', fontsize=8)
    ax3.grid(True, alpha=0.3)
    
    print("[Plot 4] Residuals vs Predicted...")
    ax4 = plt.subplot(2, 3, 4)
    ax4.scatter(y_pred, residuals, alpha=0.5, c='steelblue', s=20)
    ax4.axhline(y=0, color='green', linestyle='--', linewidth=2)
    ax4.axhline(y=mae, color='orange', linestyle=':', linewidth=1, label=f'+MAE: {mae:.2f}')
    ax4.axhline(y=-mae, color='orange', linestyle=':', linewidth=1, label=f'-MAE: {-mae:.2f}')
    ax4.set_xlabel('Predicted Price (10k CNY)', fontsize=10)
    ax4.set_ylabel('Residual', fontsize=10)
    ax4.set_title('Residuals vs Predicted Values', fontsize=12, fontweight='bold')
    ax4.legend(loc='upper right', fontsize=8)
    ax4.grid(True, alpha=0.3)
    
    print("[Plot 5] SHAP Summary Plot...")
    ax5 = plt.subplot(2, 3, 5)
    plt.sca(ax5)
    shap.summary_plot(shap_values, X_sample, show=False, plot_size=None)
    plt.title('SHAP Summary - Feature Impact', fontsize=12, fontweight='bold')
    
    print("[Plot 6] SHAP Feature Importance...")
    ax6 = plt.subplot(2, 3, 6)
    plt.sca(ax6)
    shap.summary_plot(shap_values, X_sample, plot_type='bar', show=False, plot_size=None)
    plt.title('SHAP Mean Importance', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    
    output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'shap_analysis.png')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    print(f"\n[Output] Analysis saved to: {output_path}")
    
    print("\n" + "=" * 60)
    print("  Analysis Completed!")
    print("=" * 60)
    
    print("\n[Summary]")
    print(f"  Total Boosting Rounds: {epochs}")
    print(f"  Best Validation RMSE: {min_val_rmse:.4f} (Round {min_val_epoch})")
    print(f"  Final Training RMSE: {results['validation_0']['rmse'][-1]:.4f}")
    print(f"  Final Validation RMSE: {results['validation_1']['rmse'][-1]:.4f}")
    print(f"  R2 Score: {r2:.4f}")
    print(f"  MAE: {mae:.4f} (10k CNY)")
    print(f"  Residual Mean: {residuals.mean():.4f}")
    print(f"  Residual Std: {residuals.std():.4f}")
    
    print("\n[Interpretation Guide]")
    print("  - Learning Curve: Shows model convergence over boosting rounds")
    print("  - Gap between train/val indicates overfitting level")
    print("  - Residual Distribution: Should be centered around 0")
    print("  - SHAP Summary: Red = high feature value, Blue = low")
    print("  - Right side = increases price, Left side = decreases price")

if __name__ == '__main__':
    main()
