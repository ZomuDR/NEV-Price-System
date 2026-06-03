import pandas as pd

df = pd.read_excel('static/data/car_data_15features.xlsx')

# 填补剩余空值
# 轴距 - 根据级别设置典型值
df.loc[(df['轴距(mm)'].isnull()) & (df['级别'].str.contains('紧凑型', na=False)), '轴距(mm)'] = 2700
df.loc[(df['轴距(mm)'].isnull()) & (df['级别'].str.contains('中型', na=False)), '轴距(mm)'] = 2850
df.loc[(df['轴距(mm)'].isnull()) & (df['级别'].str.contains('中大型', na=False)), '轴距(mm)'] = 3000
df['轴距(mm)'] = df['轴距(mm)'].fillna(2750)

# 最大扭矩 - 根据能源类型和马力估算
# 电动: 扭矩 = 功率 * 2.5 (估算)
mask = (df['最大扭矩(N·m)'].isnull()) & (df['电动机总功率(kW)'].notnull())
df.loc[mask, '最大扭矩(N·m)'] = df.loc[mask, '电动机总功率(kW)'] * 2.5
# 剩余用典型值
df['最大扭矩(N·m)'] = df['最大扭矩(N·m)'].fillna(300)

# 挡位数 - 电动车通常无级变速
df['挡位数'] = df['挡位数'].fillna(1)

# 宽(mm) - 根据级别设置
df.loc[(df['宽(mm)'].isnull()) & (df['级别'].str.contains('紧凑型', na=False)), '宽(mm)'] = 1800
df.loc[(df['宽(mm)'].isnull()) & (df['级别'].str.contains('中型', na=False)), '宽(mm)'] = 1850
df.loc[(df['宽(mm)'].isnull()) & (df['级别'].str.contains('中大型', na=False)), '宽(mm)'] = 1900
df['宽(mm)'] = df['宽(mm)'].fillna(1800)

# 前轮距 - 根据宽度估算
df['前轮距(mm)'] = df['前轮距(mm)'].fillna(df['宽(mm)'] * 0.65)

print('最终空值统计:')
print(df.isnull().sum().sum(), '个空值')

df.to_excel('static/data/car_data_15features.xlsx', index=False)
print('数据已保存')