from django.urls import path
from . import views

urlpatterns = [
    path('map/', views.floor_map, name='floor_map'),
    # Другие маршруты
]
