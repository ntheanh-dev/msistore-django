from django.http import Http404
from django.shortcuts import render
from rest_framework import viewsets, generics, permissions, parsers
from rest_framework.decorators import action
from rest_framework.views import Response
from .models import User, Category, Brand, Image, Product
from .serializers import (
    UserSerializer, CategorySerializer, BrandSerializer, ImageSerializer, ProductSerializer
)


class UserViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    parser_classes = [parsers.MultiPartParser, ]

    def get_permissions(self):
        if self.action in ['current_user']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    @action(methods=['get', 'put'], detail=False, url_path='current-user')
    def current_user(self, request):
        print(request.user)
        u = request.user
        if request.method.__eq__('PUT'):
            for k, v in request.data.items():
                setattr(u, k, v)
            u.save()

        return Response(UserSerializer(u, context={'request': request}).data)


class ProductViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer



class CategoryViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView, generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class BrandViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer


class ImageViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
