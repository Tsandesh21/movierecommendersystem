from django.urls import path
from .views import home,moviedetail,MovieByGenre

urlpatterns = [
    path('',home,name='homepage'),
    path('movie/<str:movie>/',moviedetail,name='moviedetail'),
    path('moviebygenres',MovieByGenre,name='moviebygenres'),
]