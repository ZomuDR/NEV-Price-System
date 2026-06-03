from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from cars.models import FavoriteCar, Car, PredictionHistory, MLModel
from cars.serializers import CarSerializer
from django.shortcuts import get_object_or_404

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_favorites(request):
    favorites = FavoriteCar.objects.filter(user=request.user).select_related('car')
    data = []
    for fav in favorites:
        car = fav.car
        data.append({
            'id': fav.id,
            'car_id': car.id,
            'model_name': car.model_name,
            'manufacturer': car.manufacturer,
            'car_class': car.car_class,
            'energy_type': car.energy_type,
            'motor_power': car.motor_power,
            'max_horsepower': car.max_horsepower,
            'max_speed': car.max_speed,
            'electric_range': car.electric_range,
            'acceleration_time': car.acceleration_time,
            'price': car.price,
            'created_at': fav.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    return Response(data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_favorite(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    favorite, created = FavoriteCar.objects.get_or_create(
        user=request.user,
        car=car
    )
    if created:
        return Response({'message': '收藏成功', 'id': favorite.id}, status=status.HTTP_201_CREATED)
    return Response({'message': '已收藏'}, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_favorite(request, car_id):
    deleted, _ = FavoriteCar.objects.filter(user=request.user, car_id=car_id).delete()
    if deleted:
        return Response({'message': '取消收藏成功'})
    return Response({'message': '未收藏该车型'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_favorite_by_id(request, favorite_id):
    deleted, _ = FavoriteCar.objects.filter(id=favorite_id, user=request.user).delete()
    if deleted:
        return Response({'message': '取消收藏成功'})
    return Response({'message': '收藏记录不存在'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_favorite(request, car_id):
    is_favorite = FavoriteCar.objects.filter(user=request.user, car_id=car_id).exists()
    return Response({'is_favorite': is_favorite})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_stats(request):
    prediction_count = PredictionHistory.objects.filter(user=request.user).count()
    favorite_count = FavoriteCar.objects.filter(user=request.user).count()
    
    return Response({
        'prediction_count': prediction_count,
        'favorite_count': favorite_count
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def get_total_stats(request):
    total_predictions = PredictionHistory.objects.count()
    total_cars = Car.objects.count()
    active_models = MLModel.objects.filter(is_active=True).count()
    
    return Response({
        'total_predictions': total_predictions,
        'total_cars': total_cars,
        'active_models': active_models
    })
