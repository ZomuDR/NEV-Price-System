from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from .models import User
from .serializers import UserAdminSerializer

class UserPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class UserAdminViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserAdminSerializer
    pagination_class = UserPagination
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        queryset = User.objects.all()
        
        search = self.request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search) |
                Q(address__icontains=search)
            )
        
        username = self.request.query_params.get('username', '')
        if username:
            queryset = queryset.filter(username=username)
        
        email = self.request.query_params.get('email', '')
        if email:
            queryset = queryset.filter(email=email)
        
        is_staff = self.request.query_params.get('is_staff', '')
        if is_staff:
            queryset = queryset.filter(is_staff=is_staff.lower() == 'true')
        
        ordering = self.request.query_params.get('ordering', 'id')
        if ordering:
            queryset = queryset.order_by(ordering)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        keyword = request.query_params.get('keyword', '')
        if keyword:
            users = User.objects.filter(
                Q(username__icontains=keyword) |
                Q(email__icontains=keyword) |
                Q(phone__icontains=keyword)
            )[:50]
        else:
            users = User.objects.all()[:50]
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)