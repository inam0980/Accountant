from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('statistics/', views.system_statistics, name='statistics'),
]
