from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views_admin import UserAdminViewSet

router = DefaultRouter()
router.register(r'admin/users', UserAdminViewSet, basename='user-admin')

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('current-user/', views.current_user, name='current_user'),
    path('profile/', views.user_profile, name='user-profile'),
    path('', include(router.urls)),
]