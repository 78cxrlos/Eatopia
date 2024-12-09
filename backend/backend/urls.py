from django.contrib import admin
from django.urls import path
from api import views

urlpatterns = [
    path('', views.base, name='base'),
    path('home', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('reviews/', views.reviews, name='reviews'),
    path('post-review/', views.post_review, name='post_review'),
]

