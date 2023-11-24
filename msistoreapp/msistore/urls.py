from django.contrib import admin
from django.urls import path, re_path, include
from rest_framework import routers
from . import views

r = routers.DefaultRouter()
r.register('users', views.UserViewSet)
r.register('category', views.CategoryViewSet)
r.register('brand', views.BrandViewSet)
r.register('products', views.ProductViewSet)
r.register('image', views.ImageViewSet)
r.register('userinfo', views.UserInfoViewSet)
r.register('order', views.OrderViewSet)
r.register('order-item', views.OrderItemViewSet)
r.register('status-order', views.StatusOrderViewSet)

urlpatterns = [
    path('', include(r.urls))
]
