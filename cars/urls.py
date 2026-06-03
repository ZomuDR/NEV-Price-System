from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CarViewSet
from .views_dashboard import dashboard_data
from .views_predict import get_models, set_active_model, delete_model, get_feature_options, predict_price, get_prediction_history, get_similar_cars
from .views_favorites import (
    get_favorites, add_favorite, remove_favorite, remove_favorite_by_id,
    check_favorite, get_user_stats, get_total_stats
)

router = DefaultRouter()
router.register(r'cars', CarViewSet, basename='car')

urlpatterns = [
    path('dashboard/', dashboard_data, name='dashboard'),
    path('models/', get_models, name='models'),
    path('models/<int:model_id>/activate/', set_active_model, name='activate_model'),
    path('models/<int:model_id>/delete/', delete_model, name='delete_model'),
    path('feature-options/', get_feature_options, name='feature_options'),
    path('predict/', predict_price, name='predict'),
    path('similar-cars/', get_similar_cars, name='similar_cars'),
    path('prediction-history/', get_prediction_history, name='prediction_history'),
    path('favorites/', get_favorites, name='favorites'),
    path('favorites/<int:car_id>/', add_favorite, name='add_favorite'),
    path('favorites/<int:car_id>/remove/', remove_favorite, name='remove_favorite'),
    path('favorites/item/<int:favorite_id>/', remove_favorite_by_id, name='remove_favorite_by_id'),
    path('favorites/check/<int:car_id>/', check_favorite, name='check_favorite'),
    path('user-stats/', get_user_stats, name='user_stats'),
    path('total-stats/', get_total_stats, name='total_stats'),
    path('', include(router.urls)),
]
