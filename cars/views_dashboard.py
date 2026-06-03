from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Count, Avg, Max, Min
from django.utils import timezone
from datetime import timedelta
from .models import Car, PredictionHistory

@api_view(['GET'])
@permission_classes([AllowAny])
def dashboard_data(request):
    total_cars = Car.objects.count()
    total_predictions = PredictionHistory.objects.count()
    
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = now - timedelta(days=now.weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    today_predictions = PredictionHistory.objects.filter(created_at__gte=today_start).count()
    week_predictions = PredictionHistory.objects.filter(created_at__gte=week_start).count()
    month_predictions = PredictionHistory.objects.filter(created_at__gte=month_start).count()
    
    manufacturer_dist = list(
        Car.objects.values('manufacturer')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )
    
    energy_type_dist = list(
        Car.objects.values('energy_type')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    
    car_class_dist = list(
        Car.objects.values('car_class')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )
    
    price_ranges = [
        {'range': '0-10万', 'count': Car.objects.filter(price__gte=0, price__lt=10).count()},
        {'range': '10-20万', 'count': Car.objects.filter(price__gte=10, price__lt=20).count()},
        {'range': '20-30万', 'count': Car.objects.filter(price__gte=20, price__lt=30).count()},
        {'range': '30-50万', 'count': Car.objects.filter(price__gte=30, price__lt=50).count()},
        {'range': '50-100万', 'count': Car.objects.filter(price__gte=50, price__lt=100).count()},
        {'range': '100万以上', 'count': Car.objects.filter(price__gte=100).count()},
    ]
    
    top_expensive = list(
        Car.objects.order_by('-price')[:3].values(
            'id', 'model_name', 'manufacturer', 'price', 'energy_type'
        )
    )
    
    top_fast = list(
        Car.objects.exclude(acceleration_time__isnull=True)
        .exclude(acceleration_time=0)
        .order_by('acceleration_time')[:3].values(
            'id', 'model_name', 'manufacturer', 'acceleration_time', 'energy_type'
        )
    )
    
    top_range = list(
        Car.objects.exclude(electric_range__isnull=True)
        .exclude(electric_range=0)
        .order_by('-electric_range')[:3].values(
            'id', 'model_name', 'manufacturer', 'electric_range', 'energy_type'
        )
    )
    
    avg_price = Car.objects.aggregate(Avg('price'))['price__avg'] or 0
    avg_motor_power = Car.objects.aggregate(Avg('motor_power'))['motor_power__avg'] or 0
    
    return Response({
        'total_cars': total_cars,
        'total_predictions': total_predictions,
        'today_predictions': today_predictions,
        'week_predictions': week_predictions,
        'month_predictions': month_predictions,
        'manufacturer_dist': manufacturer_dist,
        'energy_type_dist': energy_type_dist,
        'car_class_dist': car_class_dist,
        'price_ranges': price_ranges,
        'top_expensive': top_expensive,
        'top_fast': top_fast,
        'top_range': top_range,
        'avg_price': round(avg_price, 2),
        'avg_motor_power': round(avg_motor_power, 2),
    })