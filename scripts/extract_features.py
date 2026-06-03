import pandas as pd
import numpy as np
import re

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
print(f"原始数据形状: {df.shape}")

target_col = '经销商报价'
y = df[target_col].apply(parse_price)
df = df[~y.isna()]
y = y[~y.isna()]

top_15_features = [
    '电动机总功率(kW)',
    '最大马力(Ps)',
    '最高车速(km/h)',
    '油箱容积(L)',
    '整备质量(kg)',
    '轴距(mm)',
    '最大扭矩(N·m)',
    'NEDC综合油耗(L/100km)',
    '挡位数',
    '宽(mm)',
    '排量(mL)',
    '官方百公里加速时间(s)',
    '纯电续航里程(km)',
    '前轮距(mm)',
    '座位数(个)'
]

available_features = [f for f in top_15_features if f in df.columns]
print(f"可用特征数量: {len(available_features)}")

select_cols = ['型号', '厂商', '级别', '能源类型'] + available_features + [target_col]
select_cols = [col for col in select_cols if col in df.columns]

df_new = df[select_cols].copy()
df_new['价格(万元)'] = y.values

df_new.to_excel('static/data/car_data_15features.xlsx', index=False)
print(f"新数据已保存到 static/data/car_data_15features.xlsx")
print(f"新数据形状: {df_new.shape}")
print(f"列名: {df_new.columns.tolist()}")