from django.core.management.base import BaseCommand
from cars.models import Car, MLModel
import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import pickle

FEATURE_COLUMNS = [
    'manufacturer', 'car_class', 'energy_type',
    'motor_power', 'max_horsepower', 'max_speed', 'fuel_tank_volume',
    'curb_weight', 'wheelbase', 'max_torque', 'nedc_fuel_consumption',
    'gear_count', 'width', 'displacement', 'acceleration_time',
    'electric_range', 'front_track', 'seat_count'
]

CATEGORICAL_COLUMNS = ['manufacturer', 'car_class', 'energy_type']

class Command(BaseCommand):
    help = '训练XGBoost汽车价格预测模型'

    def add_arguments(self, parser):
        parser.add_argument('--model-version', type=str, default='1.0', help='模型版本号')
        parser.add_argument('--description', type=str, default='', help='模型描述')

    def handle(self, *args, **options):
        self.stdout.write('=' * 50)
        self.stdout.write('XGBoost 汽车价格预测模型训练')
        self.stdout.write('=' * 50)

        cars = Car.objects.all().values()
        df = pd.DataFrame(list(cars))
        self.stdout.write(f'从数据库加载 {len(df)} 条数据')

        self.stdout.write('\n数据预处理...')
        feature_df, target, label_encoders, feature_defaults = self.preprocess_data(df)
        self.stdout.write(f'特征数量: {len(feature_df.columns)}')
        self.stdout.write(f'特征列表: {list(feature_df.columns)}')

        self.stdout.write('\n开始训练模型...')
        model, metrics = self.train_model(feature_df, target)

        self.stdout.write('\n保存模型到数据库...')
        ml_model = self.save_model_to_db(
            model=model,
            label_encoders=label_encoders,
            feature_names=list(feature_df.columns),
            feature_defaults=feature_defaults,
            metrics=metrics,
            version=options['model_version'],
            description=options['description'] or f'XGBoost回归模型，R2={metrics["r2_score"]}'
        )

        self.stdout.write(self.style.SUCCESS(f'\n训练完成!'))
        self.stdout.write(self.style.SUCCESS(f'当前激活模型: {ml_model.name} v{ml_model.version}'))

    def preprocess_data(self, df):
        df = df.copy()
        
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
        
        feature_defaults = {}
        for col in feature_df.columns:
            if col not in CATEGORICAL_COLUMNS:
                median_val = feature_df[col].median()
                feature_df[col] = feature_df[col].fillna(median_val)
                feature_defaults[col] = float(median_val) if not pd.isna(median_val) else 0
        
        return feature_df, target, label_encoders, feature_defaults

    def train_model(self, feature_df, target):
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
        
        self.stdout.write(f'\n模型评估指标:')
        self.stdout.write(f'  R2 Score: {metrics["r2_score"]}')
        self.stdout.write(f'  MAE: {metrics["mae"]} 万元')
        self.stdout.write(f'  RMSE: {metrics["rmse"]} 万元')
        
        return model, metrics

    def save_model_to_db(self, model, label_encoders, feature_names, feature_defaults, metrics, version, description):
        MLModel.objects.update(is_active=False)
        
        ml_model = MLModel.objects.create(
            name='XGBoost汽车价格预测模型',
            version=version,
            model_type='XGBoost',
            feature_names=feature_names,
            feature_defaults=feature_defaults,
            metrics=metrics,
            is_active=True,
            description=description
        )
        
        ml_model.set_model(model)
        ml_model.set_label_encoders(label_encoders)
        ml_model.save()
        
        self.stdout.write(f'\n模型已保存: {ml_model.name} v{ml_model.version}')
        return ml_model