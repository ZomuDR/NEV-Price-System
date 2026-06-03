from django.core.management.base import BaseCommand
from cars.models import Car
import pandas as pd
import re

class Command(BaseCommand):
    help = 'Import car data from Excel file'

    def handle(self, *args, **options):
        self.stdout.write('Loading Excel file...')
        df = pd.read_excel('static/data/car_data_15features.xlsx')
        
        count = 0
        for _, row in df.iterrows():
            try:
                Car.objects.create(
                    model_name=str(row.get('型号', '')),
                    manufacturer=str(row.get('厂商', '')),
                    car_class=str(row.get('级别', '')),
                    energy_type=str(row.get('能源类型', '')),
                    motor_power=self.parse_float(row.get('电动机总功率(kW)')),
                    max_horsepower=self.parse_int(row.get('最大马力(Ps)')),
                    max_speed=self.parse_int(row.get('最高车速(km/h)')),
                    fuel_tank_volume=self.parse_float(row.get('油箱容积(L)')),
                    curb_weight=self.parse_int(row.get('整备质量(kg)')),
                    wheelbase=self.parse_int(row.get('轴距(mm)')),
                    max_torque=self.parse_int(row.get('最大扭矩(N·m)')),
                    nedc_fuel_consumption=self.parse_float(row.get('NEDC综合油耗(L/100km)')),
                    gear_count=self.parse_int(row.get('挡位数')),
                    width=self.parse_int(row.get('宽(mm)')),
                    displacement=self.parse_int(row.get('排量(mL)')),
                    acceleration_time=self.parse_float(row.get('官方百公里加速时间(s)')),
                    electric_range=self.parse_int(row.get('纯电续航里程(km)')),
                    front_track=self.parse_int(row.get('前轮距(mm)')),
                    seat_count=self.parse_int(row.get('座位数(个)')),
                    price=float(row.get('价格(万元)', 0))
                )
                count += 1
            except Exception as e:
                self.stdout.write(f'Error: {e}')
                continue
        
        self.stdout.write(self.style.SUCCESS(f'Successfully imported {count} car records'))

    def parse_float(self, value):
        if pd.isna(value):
            return None
        try:
            return float(value)
        except:
            return None

    def parse_int(self, value):
        if pd.isna(value):
            return None
        try:
            return int(float(value))
        except:
            return None