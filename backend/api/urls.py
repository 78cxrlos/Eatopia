from django.contrib import admin
from django.urls import path
from api import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Homepage route, you should use only one path for home
    path('', views.home, name='home'),  

    # Restaurant Detail route
    path('restaurant/<int:restaurant_id>/', views.restaurant_detail, name='restaurant_detail'),
    
    # Auth routes
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Profile and reviews
    path('profile/', views.profile, name='profile'),
    path('reviews/', views.reviews, name='reviews'),
    path('post-review/', views.post_review, name='post_review'),
    
    # Cart routes
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:dish_id>/', views.add_to_cart, name='add_to_cart'),
    
    # Manage Orders and Add Dish routes
    path('manage-order/', views.manage_order, name='manage_order'),
    path('add-dish/', views.add_dish, name='add_dish'),
    
    # View Dishes route
    path('view-dishes/', views.view_dishes, name='view_dishes'),

    path('proceed-to-checkout/', views.proceed_to_checkout, name='proceed_to_checkout'),
    path('order-status/', views.order_status, name='order_status'),
]

# Media files configuration for serving images or files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
