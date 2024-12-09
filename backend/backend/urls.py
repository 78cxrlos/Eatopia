from django.contrib import admin
from django.urls import path
from api import views

urlpatterns = [
    path('', views.base, name='base'),
    path('', views.home, name='home'),
]

