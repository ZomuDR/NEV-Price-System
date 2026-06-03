import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'NEV_Price_System.settings'
import django
django.setup()

from cars.models import MLModel, Car
import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import pickle

print("=" * 60)
print("XGBoost 汽车价格预测模型 - 详细评估报告")
print("=" * 60)

# 获取当前激活的模型
model_obj = MLModel.objects.filter(is_active=True).first()

if model_obj:
    print("\n【模型基本信息】")
    print(f"  模型名称: {model_obj.name}")
    print(f"  版本: {model_obj.version}")
    print(f"  类型: {model_obj.model_type}")
    print(f"  创建时间: {model_obj.created_at}")
    print(f"  描述: {model_obj.description}")
    
    print("\n【模型评估指标】")
    metrics = model_obj.metrics
    r2 = metrics.get('r2_score', 0)
    mae = metrics.get('mae', 0)
    rmse = metrics.get('rmse', 0)
    
    print(f"  R2 Score (决定系数): {r2}")
    print(f"  MAE (平均绝对误差): {mae} 万元")
    print(f"  RMSE (均方根误差): {rmse} 万元")
    print(f"  训练样本数: {metrics.get('train_size', 'N/A')}")
    print(f"  测试样本数: {metrics.get('test_size', 'N/A')}")
    
    # 数据库统计
    print("\n【数据集统计】")
    total_cars = Car.objects.count()
    print(f"  总车型数: {total_cars}")
    
    cars = Car.objects.all().values('price')
    df = pd.DataFrame(list(cars))
    
    print(f"  价格范围: {df['price'].min():.2f} - {df['price'].max():.2f} 万元")
    print(f"  平均价格: {df['price'].mean():.2f} 万元")
    print(f"  价格中位数: {df['price'].median():.2f} 万元")
    print(f"  价格标准差: {df['price'].std():.2f} 万元")
    
    # 模型准确性分析
    print("\n【模型准确性分析】")
    
    # R² 解释
    if r2 >= 0.9:
        r2_level = "优秀"
        r2_desc = "模型能解释90%以上的价格变异"
    elif r2 >= 0.8:
        r2_level = "良好"
        r2_desc = "模型能解释80%-90%的价格变异"
    elif r2 >= 0.7:
        r2_level = "一般"
        r2_desc = "模型能解释70%-80%的价格变异"
    else:
        r2_level = "较差"
        r2_desc = "模型解释能力有限"
    
    print(f"  R2 评估: {r2_level} - {r2_desc}")
    
    # MAE 解释
    avg_price = df['price'].mean()
    mae_percent = (mae / avg_price) * 100
    print(f"  MAE占平均价格比例: {mae_percent:.2f}%")
    print(f"  平均预测偏差: 约 {mae:.2f} 万元")
    
    # RMSE vs MAE
    print(f"  RMSE/MAE比值: {rmse/mae:.2f}")
    if rmse / mae > 1.5:
        print("  存在较大的预测误差离群点")
    else:
        print("  预测误差分布相对均匀")
    
    # 实际预测测试
    print("\n【实际预测测试】")
    model = model_obj.get_model()
    label_encoders = model_obj.get_label_encoders()
    feature_names = model_obj.feature_names
    
    # 随机选择5辆车进行预测对比
    sample_cars = list(Car.objects.order_by('?')[:5].values())
    
    print("  随机抽样预测对比:")
    print("  " + "-" * 80)
    print(f"  {'车型':<30} {'实际价格':>10} {'预测价格':>10} {'误差':>10} {'误差率':>10}")
    print("  " + "-" * 80)
    
    total_error = 0
    for car in sample_cars:
        feature_values = []
        for col in feature_names:
            value = car.get(col, 0)
            if col in ['manufacturer', 'car_class', 'energy_type'] and col in label_encoders:
                le = label_encoders[col]
                if value in le.classes_:
                    value = le.transform([value])[0]
                else:
                    value = 0
            feature_values.append(float(value) if value else 0)
        
        X = np.array([feature_values])
        predicted = model.predict(X)[0]
        actual = car['price']
        error = abs(predicted - actual)
        error_rate = (error / actual) * 100
        total_error += error_rate
        
        model_name = car['model_name'][:28] if len(car['model_name']) > 28 else car['model_name']
        print(f"  {model_name:<30} {actual:>10.2f} {predicted:>10.2f} {error:>10.2f} {error_rate:>9.1f}%")
    
    avg_error_rate = total_error / 5
    print("  " + "-" * 80)
    print(f"  平均误差率: {avg_error_rate:.1f}%")
    
    # 结论
    print("\n【综合评价】")
    if r2 >= 0.85 and avg_error_rate < 20:
        print("  模型整体表现良好，预测结果具有较高参考价值")
        print("  建议: 可用于辅助定价决策，但需结合市场实际情况")
    elif r2 >= 0.75:
        print("  模型表现中等，预测结果有一定参考价值")
        print("  建议: 可作为价格参考，但需谨慎使用")
    else:
        print("  模型表现一般，预测准确性有待提高")
        print("  建议: 需要更多数据或特征工程优化")
    
    print("\n【改进建议】")
    print("  1. 增加更多特征: 如品牌溢价、配置等级、市场热度等")
    print("  2. 数据清洗: 处理异常值和缺失值")
    print("  3. 特征工程: 创建更有预测力的组合特征")
    print("  4. 模型调参: 优化超参数提高性能")
    print("  5. 集成学习: 结合多个模型提高稳定性")

else:
    print("没有找到激活的模型")

print("\n" + "=" * 60)