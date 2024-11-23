from django.urls import path
from . import views

urlpatterns = [
    path('map/<int:floor>/', views.floor_map, name='floor_map'),  # Маршрут для карты этажа
]
