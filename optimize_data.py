"""
根据能源类型优化车型数据
- 纯电动汽车：清除油耗、油箱容积、排量等燃油车特有字段
- 插电式混合动力/增程式：保留油耗和纯电续航（混动特性）
- 氢燃料电池：清除油耗，保留纯电续航
"""

from django.db import models
from cars.models import Car

def optimize_car_data():
    print("开始优化车型数据...")
    
    # 纯电动汽车：清除油耗、油箱容积、排量数据
    bev_count = Car.objects.filter(energy_type='纯电动').update(
        fuel_tank_volume=None,
        nedc_fuel_consumption=None,
        displacement=None
    )
    print(f"已优化 {bev_count} 辆纯电动汽车的油耗相关数据")
    
    # 氢燃料电池：清除油耗、油箱容积（氢气罐不同）
    h2_count = Car.objects.filter(energy_type='氢燃料电池').update(
        fuel_tank_volume=None,
        nedc_fuel_consumption=None,
        displacement=None
    )
    print(f"已优化 {h2_count} 辆氢燃料电池汽车的油耗相关数据")
    
    # 插电式混合动力：保留所有数据（既有电机也有发动机）
    # 增程式：保留所有数据（既有电机也有发动机）
    
    # 统计各能源类型数量
    print("\n当前数据库车型统计：")
    energy_types = Car.objects.values('energy_type').annotate(count=models.Count('id'))
    for item in energy_types:
        print(f"  {item['energy_type']}: {item['count']} 辆")
    
    # 显示优化后的数据示例
    print("\n纯电动汽车示例（应无油耗数据）：")
    bev_example = Car.objects.filter(energy_type='纯电动').first()
    if bev_example:
        print(f"  车型: {bev_example.model_name}")
        print(f"  油耗: {bev_example.nedc_fuel_consumption}")
        print(f"  油箱: {bev_example.fuel_tank_volume}")
        print(f"  排量: {bev_example.displacement}")
        print(f"  续航: {bev_example.electric_range}")

if __name__ == '__main__':
    optimize_car_data()