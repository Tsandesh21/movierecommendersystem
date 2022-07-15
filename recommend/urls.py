from django.urls import path
from .views import home,moviedetail

urlpatterns = [
    path('',home,name='homepage'),
    path('movie/<str:movie>/',moviedetail,name='moviedetail')
]