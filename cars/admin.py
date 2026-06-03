from django.contrib import admin
from .models import Car, MLModel, PredictionHistory, FavoriteCar

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ['id', 'model_name', 'manufacturer', 'car_class', 'energy_type', 'price', 'created_at']
    list_filter = ['energy_type', 'car_class', 'manufacturer']
    search_fields = ['model_name', 'manufacturer']
    ordering = ['-id']
    list_per_page = 20

@admin.register(MLModel)
class MLModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'version', 'model_type', 'is_active', 'created_at']
    list_filter = ['is_active', 'model_type']
    search_fields = ['name', 'version']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'model_data', 'label_encoders']

@admin.register(PredictionHistory)
class PredictionHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'predicted_price', 'model_used', 'user', 'created_at']
    list_filter = ['model_used', 'created_at']
    ordering = ['-created_at']
    readonly_fields = ['created_at']

@admin.register(FavoriteCar)
class FavoriteCarAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'car', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'car__model_name']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
