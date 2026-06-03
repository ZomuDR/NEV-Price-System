from django.core.management.base import BaseCommand
from cars.models import Car
from django.db.models import Avg, Max, Min

class Command(BaseCommand):
    help = 'Fill missing data in car database'

    def handle(self, *args, **options):
        cars = Car.objects.all()
        total = cars.count()
        
        numeric_fields = [
            'motor_power', 'max_horsepower', 'max_speed', 'fuel_tank_volume',
            'curb_weight', 'wheelbase', 'max_torque', 'nedc_fuel_consumption',
            'gear_count', 'width', 'displacement', 'acceleration_time',
            'electric_range', 'front_track', 'seat_count'
        ]
        
        self.stdout.write('开始填补缺失数据...')
        
        for field in numeric_fields:
            null_count = cars.filter(**{f'{field}__isnull': True}).count()
            if null_count == 0:
                continue
                
            avg_value = cars.exclude(**{f'{field}__isnull': True}).aggregate(Avg(field))[f'{field}__avg']
            
            if avg_value:
                filled = cars.filter(**{f'{field}__isnull': True}).update(**{field: round(avg_value, 1)})
                self.stdout.write(f'{field}: 填补了 {filled} 条记录 (使用平均值 {round(avg_value, 2)})')
            else:
                filled = cars.filter(**{f'{field}__isnull': True}).update(**{field: 0})
                self.stdout.write(f'{field}: 填补了 {filled} 条记录 (使用默认值 0)')
        
        self.stdout.write(self.style.SUCCESS(f'数据填补完成！共处理 {total} 条记录'))