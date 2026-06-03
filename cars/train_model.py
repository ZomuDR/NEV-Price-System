import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NEV_Price_System.settings')
django.setup()

import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from cars.models import Car, MLModel
import pickle

FEATURE_COLUMNS = [
    'manufacturer', 'car_class', 'energy_type',
    'motor_power', 'max_horsepower', 'max_speed', 'fuel_tank_volume',
    'curb_weight', 'wheelbase', 'max_torque', 'nedc_fuel_consumption',
    'gear_count', 'width', 'displacement', 'acceleration_time',
    'electric_range', 'front_track', 'seat_count'
]

CATEGORICAL_COLUMNS = ['manufacturer', 'car_class', 'energy_type']

def load_data_from_db():
    cars = Car.objects.all().values()
    df = pd.DataFrame(list(cars))
    print(f"从数据库加载 {len(df)} 条数据")
    return df

def preprocess_data(df):
    df = df.copy()
    
    feature_df = df[FEATURE_COLUMNS].copy()
    target = df['price'].values
    
    label_encoders = {}
    for col in CATEGORICAL_COLUMNS:
        if col in feature_df.columns:
            le = LabelEncoder()
            feature_df[col] = feature_df[col].fillna('Unknown')
            feature_df[col] = le.fit_transform(feature_df[col].astype(str))
            label_encoders[col] = le
    
    for col in feature_df.columns:
        if col not in CATEGORICAL_COLUMNS:
            feature_df[col] = feature_df[col].fillna(feature_df[col].median())
    
    return feature_df, target, label_encoders

def train_model(feature_df, target):
    X_train, X_test, y_train, y_test = train_test_split(
        feature_df, target, test_size=0.2, random_state=42
    )
    
    model = XGBRegressor(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    
    metrics = {
        'r2_score': round(r2_score(y_test, y_pred), 4),
        'mae': round(mean_absolute_error(y_test, y_pred), 4),
        'rmse': round(np.sqrt(mean_squared_error(y_test, y_pred)), 4),
        'train_size': len(X_train),
        'test_size': len(X_test)
    }
    
    print(f"\n模型评估指标:")
    print(f"  R² Score: {metrics['r2_score']}")
    print(f"  MAE: {metrics['mae']} 万元")
    print(f"  RMSE: {metrics['rmse']} 万元")
    
    return model, metrics

def save_model_to_db(model, label_encoders, feature_names, metrics, version='1.0', description=''):
    MLModel.objects.update(is_active=False)
    
    ml_model = MLModel.objects.create(
        name='XGBoost汽车价格预测模型',
        version=version,
        model_type='XGBoost',
        feature_names=feature_names,
        metrics=metrics,
        is_active=True,
        description=description or f"XGBoost回归模型，R²={metrics['r2_score']}"
    )
    
    ml_model.set_model(model)
    ml_model.set_label_encoders(label_encoders)
    ml_model.save()
    
    print(f"\n模型已保存: {ml_model.name} v{ml_model.version}")
    return ml_model

def main():
    print("=" * 50)
    print("XGBoost 汽车价格预测模型训练")
    print("=" * 50)
    
    df = load_data_from_db()
    
    print("\n数据预处理...")
    feature_df, target, label_encoders = preprocess_data(df)
    print(f"特征数量: {len(feature_df.columns)}")
    print(f"特征列表: {list(feature_df.columns)}")
    
    print("\n开始训练模型...")
    model, metrics = train_model(feature_df, target)
    
    print("\n保存模型到数据库...")
    ml_model = save_model_to_db(
        model=model,
        label_encoders=label_encoders,
        feature_names=list(feature_df.columns),
        metrics=metrics,
        version='1.0',
        description='初始版本，使用全部15个特征训练'
    )
    
    print("\n训练完成!")
    print(f"当前激活模型: {ml_model.name} v{ml_model.version}")
    
    return ml_model

if __name__ == '__main__':
    main()