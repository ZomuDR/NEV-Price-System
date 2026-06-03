from django.db import models
import pickle
import base64

class MLModel(models.Model):
    name = models.CharField(max_length=100, verbose_name='模型名称')
    version = models.CharField(max_length=50, verbose_name='模型版本')
    model_type = models.CharField(max_length=50, default='XGBoost', verbose_name='模型类型')
    model_data = models.BinaryField(verbose_name='模型二进制数据')
    feature_names = models.JSONField(default=list, verbose_name='特征名称列表')
    label_encoders = models.BinaryField(null=True, blank=True, verbose_name='标签编码器')
    feature_defaults = models.JSONField(default=dict, verbose_name='特征默认值')
    metrics = models.JSONField(default=dict, verbose_name='模型评估指标')
    is_active = models.BooleanField(default=False, verbose_name='是否激活')
    description = models.TextField(blank=True, verbose_name='模型描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'cars_mlmodel'
        verbose_name = '机器学习模型'
        verbose_name_plural = '机器学习模型'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} v{self.version}"

    def set_model(self, model_obj):
        self.model_data = pickle.dumps(model_obj)

    def get_model(self):
        return pickle.loads(self.model_data)

    def set_label_encoders(self, encoders_dict):
        self.label_encoders = pickle.dumps(encoders_dict)

    def get_label_encoders(self):
        if self.label_encoders:
            return pickle.loads(self.label_encoders)
        return {}


class PredictionHistory(models.Model):
    input_features = models.JSONField(verbose_name='输入特征')
    predicted_price = models.FloatField(verbose_name='预测价格(万元)')
    model_used = models.ForeignKey(MLModel, on_delete=models.SET_NULL, null=True, verbose_name='使用的模型')
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='用户')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='预测时间')

    class Meta:
        db_table = 'cars_prediction_history'
        verbose_name = '预测历史'
        verbose_name_plural = '预测历史'
        ordering = ['-created_at']

    def __str__(self):
        return f"预测: {self.predicted_price:.2f}万"


class Car(models.Model):
    model_name = models.CharField(max_length=200, verbose_name='型号')
    manufacturer = models.CharField(max_length=100, verbose_name='厂商')
    car_class = models.CharField(max_length=50, verbose_name='级别')
    energy_type = models.CharField(max_length=20, verbose_name='能源类型')
    
    motor_power = models.FloatField(null=True, blank=True, verbose_name='电动机总功率(kW)')
    max_horsepower = models.IntegerField(null=True, blank=True, verbose_name='最大马力(Ps)')
    max_speed = models.IntegerField(null=True, blank=True, verbose_name='最高车速(km/h)')
    fuel_tank_volume = models.FloatField(null=True, blank=True, verbose_name='油箱容积(L)')
    curb_weight = models.IntegerField(null=True, blank=True, verbose_name='整备质量(kg)')
    wheelbase = models.IntegerField(null=True, blank=True, verbose_name='轴距(mm)')
    max_torque = models.IntegerField(null=True, blank=True, verbose_name='最大扭矩(N·m)')
    nedc_fuel_consumption = models.FloatField(null=True, blank=True, verbose_name='NEDC综合油耗(L/100km)')
    gear_count = models.IntegerField(null=True, blank=True, verbose_name='挡位数')
    width = models.IntegerField(null=True, blank=True, verbose_name='宽(mm)')
    displacement = models.IntegerField(null=True, blank=True, verbose_name='排量(mL)')
    acceleration_time = models.FloatField(null=True, blank=True, verbose_name='官方百公里加速时间(s)')
    electric_range = models.IntegerField(null=True, blank=True, verbose_name='纯电续航里程(km)')
    front_track = models.IntegerField(null=True, blank=True, verbose_name='前轮距(mm)')
    seat_count = models.IntegerField(null=True, blank=True, verbose_name='座位数(个)')
    
    price = models.FloatField(verbose_name='价格(万元)')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'cars_car'
        verbose_name = '汽车数据'
        verbose_name_plural = '汽车数据'
        ordering = ['-id']

    def __str__(self):
        return self.model_name


class FavoriteCar(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name='用户')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name='车型')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='收藏时间')

    class Meta:
        db_table = 'cars_favorite_car'
        verbose_name = '收藏车型'
        verbose_name_plural = '收藏车型'
        ordering = ['-created_at']
        unique_together = ['user', 'car']

    def __str__(self):
        return f"{self.user.username} - {self.car.model_name}"