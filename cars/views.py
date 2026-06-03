from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from .models import Car
from .serializers import CarSerializer, CarCreateSerializer, CarUpdateSerializer

class CarPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    pagination_class = CarPagination
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CarCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return CarUpdateSerializer
        return CarSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'search']:
            return [AllowAny()]
        return [IsAdminUser()]
    
    def get_queryset(self):
        queryset = Car.objects.all()
        
        search = self.request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(model_name__icontains=search) |
                Q(manufacturer__icontains=search) |
                Q(car_class__icontains=search) |
                Q(energy_type__icontains=search) |
                Q(motor_power__icontains=search) |
                Q(max_horsepower__icontains=search) |
                Q(max_speed__icontains=search) |
                Q(price__icontains=search)
            )
        
        model_name = self.request.query_params.get('model_name', '')
        if model_name:
            queryset = queryset.filter(model_name=model_name)
        
        manufacturer = self.request.query_params.get('manufacturer', '')
        if manufacturer:
            queryset = queryset.filter(manufacturer=manufacturer)
        
        car_class = self.request.query_params.get('car_class', '')
        if car_class:
            queryset = queryset.filter(car_class=car_class)
        
        energy_type = self.request.query_params.get('energy_type', '')
        if energy_type:
            queryset = queryset.filter(energy_type=energy_type)
        
        ordering = self.request.query_params.get('ordering', 'id')
        if ordering:
            queryset = queryset.order_by(ordering)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        keyword = request.query_params.get('keyword', '')
        if keyword:
            cars = Car.objects.filter(
                Q(model_name__icontains=keyword) |
                Q(manufacturer__icontains=keyword) |
                Q(car_class__icontains=keyword) |
                Q(energy_type__icontains=keyword)
            )[:50]
        else:
            cars = Car.objects.all()[:50]
        serializer = self.get_serializer(cars, many=True)
        return Response(serializer.data)
