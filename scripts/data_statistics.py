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
from cars.models import Car
from xgboost import XGBRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import warnings
warnings.filterwarnings('ignore')

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

FEATURE_COLUMNS = [
    'manufacturer', 'car_class', 'energy_type',
    'motor_power', 'max_horsepower', 'max_speed', 'fuel_tank_volume',
    'curb_weight', 'wheelbase', 'max_torque', 'nedc_fuel_consumption',
    'gear_count', 'width', 'displacement', 'acceleration_time',
    'electric_range', 'front_track', 'seat_count'
]

NUMERIC_COLUMNS = [
    'motor_power', 'max_horsepower', 'max_speed', 'fuel_tank_volume',
    'curb_weight', 'wheelbase', 'max_torque', 'nedc_fuel_consumption',
    'gear_count', 'width', 'displacement', 'acceleration_time',
    'electric_range', 'front_track', 'seat_count'
]

CATEGORICAL_COLUMNS = ['manufacturer', 'car_class', 'energy_type']

def main():
    print("=" * 60)
    print("  Data Statistics & Feature Importance Analysis")
    print("=" * 60)
    
    cars = Car.objects.all().values()
    df = pd.DataFrame(list(cars))
    print(f"\n[Data] Total records: {len(df)}")
    
    df_filtered = df.dropna(subset=['price'])
    df_filtered = df_filtered[df_filtered['price'] > 0]
    print(f"[Data] After filtering (price > 0): {len(df_filtered)} records")
    
    for col in NUMERIC_COLUMNS:
        if col in df_filtered.columns:
            df_filtered[col] = pd.to_numeric(df_filtered[col], errors='coerce')
    
    fig = plt.figure(figsize=(20, 16))
    fig.suptitle('Data Statistics & Feature Importance Analysis', fontsize=18, fontweight='bold', y=1.02)
    
    print("\n[Plot 1] Price Distribution...")
    ax1 = plt.subplot(3, 3, 1)
    ax1.hist(df_filtered['price'], bins=50, color='steelblue', edgecolor='white', alpha=0.7)
    ax1.axvline(df_filtered['price'].mean(), color='red', linestyle='--', label=f'Mean: {df_filtered["price"].mean():.1f}')
    ax1.axvline(df_filtered['price'].median(), color='green', linestyle='--', label=f'Median: {df_filtered["price"].median():.1f}')
    ax1.set_xlabel('Price (10k CNY)')
    ax1.set_ylabel('Count')
    ax1.set_title('Price Distribution')
    ax1.legend()
    
    print("[Plot 2] Energy Type Distribution...")
    ax2 = plt.subplot(3, 3, 2)
    energy_counts = df_filtered['energy_type'].value_counts()
    colors = plt.cm.Set2(np.linspace(0, 1, len(energy_counts)))
    ax2.pie(energy_counts.values, labels=energy_counts.index, autopct='%1.1f%%', colors=colors)
    ax2.set_title('Energy Type Distribution')
    
    print("[Plot 3] Car Class Distribution...")
    ax3 = plt.subplot(3, 3, 3)
    class_counts = df_filtered['car_class'].value_counts().head(10)
    ax3.barh(range(len(class_counts)), class_counts.values, color='teal')
    ax3.set_yticks(range(len(class_counts)))
    ax3.set_yticklabels(class_counts.index, fontsize=8)
    ax3.set_xlabel('Count')
    ax3.set_title('Top 10 Car Classes')
    
    print("[Plot 4] Numeric Features Statistics (Before vs After Filtering)...")
    ax4 = plt.subplot(3, 3, 4)
    numeric_stats = []
    for col in NUMERIC_COLUMNS[:8]:
        original_count = df[col].notna().sum()
        filtered_count = df_filtered[col].notna().sum()
        numeric_stats.append({'Feature': col[:10], 'Original': original_count, 'Filtered': filtered_count})
    
    stats_df = pd.DataFrame(numeric_stats)
    x = np.arange(len(stats_df))
    width = 0.35
    ax4.bar(x - width/2, stats_df['Original'], width, label='Original', color='steelblue')
    ax4.bar(x + width/2, stats_df['Filtered'], width, label='Filtered', color='coral')
    ax4.set_xticks(x)
    ax4.set_xticklabels(stats_df['Feature'], rotation=45, ha='right', fontsize=8)
    ax4.set_ylabel('Non-null Count')
    ax4.set_title('Data Completeness')
    ax4.legend()
    
    print("[Plot 5] Correlation Heatmap (Top Features)...")
    ax5 = plt.subplot(3, 3, 5)
    corr_cols = ['price', 'motor_power', 'curb_weight', 'wheelbase', 'max_horsepower', 'electric_range']
    corr_matrix = df_filtered[corr_cols].corr()
    im = ax5.imshow(corr_matrix, cmap='RdBu_r', aspect='auto', vmin=-1, vmax=1)
    ax5.set_xticks(range(len(corr_cols)))
    ax5.set_yticks(range(len(corr_cols)))
    ax5.set_xticklabels([c[:8] for c in corr_cols], rotation=45, ha='right', fontsize=8)
    ax5.set_yticklabels([c[:8] for c in corr_cols], fontsize=8)
    ax5.set_title('Correlation Heatmap')
    plt.colorbar(im, ax=ax5)
    
    print("[Plot 6] Price by Energy Type...")
    ax6 = plt.subplot(3, 3, 6)
    energy_types = df_filtered['energy_type'].unique()
    box_data = [df_filtered[df_filtered['energy_type'] == et]['price'].values for et in energy_types]
    bp = ax6.boxplot(box_data, labels=energy_types, patch_artist=True)
    colors_box = plt.cm.Set3(np.linspace(0, 1, len(energy_types)))
    for patch, color in zip(bp['boxes'], colors_box):
        patch.set_facecolor(color)
    ax6.set_ylabel('Price (10k CNY)')
    ax6.set_title('Price by Energy Type')
    ax6.tick_params(axis='x', rotation=15)
    
    print("[Plot 7] XGBoost Feature Importance...")
    ax7 = plt.subplot(3, 3, 7)
    
    feature_df = df_filtered[FEATURE_COLUMNS].copy()
    target = df_filtered['price'].values
    
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
    
    xgb_model = XGBRegressor(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, n_jobs=-1)
    xgb_model.fit(X_train, y_train)
    
    xgb_importance = xgb_model.feature_importances_
    indices = np.argsort(xgb_importance)[::-1]
    
    colors_xgb = plt.cm.viridis(np.linspace(0.2, 0.8, len(FEATURE_COLUMNS)))
    ax7.barh(range(len(FEATURE_COLUMNS)), xgb_importance[indices][::-1], color=colors_xgb[::-1])
    ax7.set_yticks(range(len(FEATURE_COLUMNS)))
    ax7.set_yticklabels([FEATURE_COLUMNS[i][:12] for i in indices[::-1]], fontsize=7)
    ax7.set_xlabel('Importance')
    ax7.set_title('XGBoost Feature Importance')
    
    print("[Plot 8] Random Forest Feature Importance...")
    ax8 = plt.subplot(3, 3, 8)
    
    rf_model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    rf_model.fit(X_train, y_train)
    
    rf_importance = rf_model.feature_importances_
    indices_rf = np.argsort(rf_importance)[::-1]
    
    colors_rf = plt.cm.plasma(np.linspace(0.2, 0.8, len(FEATURE_COLUMNS)))
    ax8.barh(range(len(FEATURE_COLUMNS)), rf_importance[indices_rf][::-1], color=colors_rf[::-1])
    ax8.set_yticks(range(len(FEATURE_COLUMNS)))
    ax8.set_yticklabels([FEATURE_COLUMNS[i][:12] for i in indices_rf[::-1]], fontsize=7)
    ax8.set_xlabel('Importance')
    ax8.set_title('Random Forest Feature Importance')
    
    print("[Plot 9] Feature Importance Comparison...")
    ax9 = plt.subplot(3, 3, 9)
    
    top_n = 10
    xgb_top = set([FEATURE_COLUMNS[i] for i in indices[:top_n]])
    rf_top = set([FEATURE_COLUMNS[i] for i in indices_rf[:top_n]])
    common = xgb_top & rf_top
    
    x_pos = np.arange(top_n)
    width = 0.35
    
    xgb_top_features = [FEATURE_COLUMNS[i] for i in indices[:top_n]]
    rf_importance_aligned = [rf_importance[FEATURE_COLUMNS.index(f)] for f in xgb_top_features]
    
    ax9.bar(x_pos - width/2, [xgb_importance[FEATURE_COLUMNS.index(f)] for f in xgb_top_features], 
            width, label='XGBoost', color='steelblue')
    ax9.bar(x_pos + width/2, rf_importance_aligned, width, label='RandomForest', color='coral')
    ax9.set_xticks(x_pos)
    ax9.set_xticklabels([f[:8] for f in xgb_top_features], rotation=45, ha='right', fontsize=8)
    ax9.set_ylabel('Importance')
    ax9.set_title('Top 10 Features Comparison')
    ax9.legend()
    
    plt.tight_layout()
    
    output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'data_statistics.png')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    print(f"\n[Output] Statistics saved to: {output_path}")
    
    print("\n" + "=" * 60)
    print("  Analysis Summary")
    print("=" * 60)
    
    print(f"\n[Data Statistics]")
    print(f"  Total records: {len(df)}")
    print(f"  Filtered records: {len(df_filtered)}")
    print(f"  Price range: {df_filtered['price'].min():.2f} - {df_filtered['price'].max():.2f} (10k CNY)")
    print(f"  Mean price: {df_filtered['price'].mean():.2f} (10k CNY)")
    print(f"  Median price: {df_filtered['price'].median():.2f} (10k CNY)")
    
    print(f"\n[Top 5 Important Features - XGBoost]")
    for i in range(5):
        print(f"  {i+1}. {FEATURE_COLUMNS[indices[i]]}: {xgb_importance[indices[i]]:.4f}")
    
    print(f"\n[Top 5 Important Features - Random Forest]")
    for i in range(5):
        print(f"  {i+1}. {FEATURE_COLUMNS[indices_rf[i]]}: {rf_importance[indices_rf[i]]:.4f}")
    
    print("\n" + "=" * 60)
    print("  Analysis Completed!")
    print("=" * 60)

if __name__ == '__main__':
    main()
