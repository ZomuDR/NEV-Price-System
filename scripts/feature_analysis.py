import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import warnings
import re
warnings.filterwarnings('ignore')

def parse_price(price_str):
    if pd.isna(price_str):
        return np.nan
    if isinstance(price_str, (int, float)):
        return float(price_str)
    price_str = str(price_str)
    match = re.search(r'([\d.]+)', price_str)
    if match:
        return float(match.group(1))
    return np.nan

print("正在加载数据...")
df = pd.read_excel('static/data/car_data.xlsx')
print(f"数据形状: {df.shape}")

target_col = '经销商报价'
if target_col not in df.columns:
    target_col = '官方指导价'

print(f"目标变量: {target_col}")

y = df[target_col].apply(parse_price)
df = df[~y.isna()]
y = y[~y.isna()]

print(f"去除空值后数据形状: {df.shape}")

exclude_cols = ['Unnamed: 0', '型号', target_col, '官方指导价']
feature_cols = [col for col in df.columns if col not in exclude_cols]

X = df[feature_cols].copy()

print(f"特征数量: {len(feature_cols)}")

for col in X.columns:
    if X[col].dtype == 'object':
        le = LabelEncoder()
        X[col] = X[col].fillna('Unknown')
        X[col] = le.fit_transform(X[col].astype(str))
    else:
        try:
            X[col] = pd.to_numeric(X[col], errors='coerce')
            X[col] = X[col].fillna(X[col].median())
        except:
            X[col] = X[col].fillna(0)

X = X.apply(pd.to_numeric, errors='coerce').fillna(0)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("正在训练XGBoost模型...")
model = XGBRegressor(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    random_state=42,
    n_jobs=-1
)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

r2 = r2_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

print("\n" + "="*60)
print("模型评估指标:")
print("="*60)
print(f"R² 决定系数:           {r2:.4f}")
print(f"MAE 平均绝对误差:      {mae:.4f} 万元")
print(f"RMSE 均方根误差:       {rmse:.4f} 万元")
print(f"平均预测误差率:        {mae / y_test.mean() * 100:.2f}%")

print("\n" + "="*60)
print("模型解释:")
print("="*60)
if r2 >= 0.9:
    print("模型效果: 优秀 (R² >= 0.9)")
elif r2 >= 0.8:
    print("模型效果: 良好 (0.8 <= R² < 0.9)")
elif r2 >= 0.7:
    print("模型效果: 中等 (0.7 <= R² < 0.8)")
else:
    print("模型效果: 较差 (R² < 0.7)")

print("\n正在计算特征重要性...")
feature_importance = pd.DataFrame({
    'feature': feature_cols,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

top_15 = feature_importance.head(15)

print("\n" + "="*60)
print("最具影响力的15个特征:")
print("="*60)
for idx, (i, row) in enumerate(top_15.iterrows()):
    print(f"{idx+1:2d}. {row['feature']:<40} 重要性: {row['importance']:.4f}")

top_15.to_excel('static/data/top15_features.xlsx', index=False)
print("\n结果已保存到 static/data/top15_features.xlsx")