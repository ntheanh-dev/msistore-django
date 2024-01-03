from django.db import transaction
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from rest_framework import viewsets, generics, permissions, parsers, status
from rest_framework.decorators import action
from rest_framework.views import Response
from .models import User, Category, Brand, Image, Product, Like, UserInfo, Order, OrderItem, StatusOrder
from .pagination import CustomPagination
from .serializers import (
    UserSerializer, CategorySerializer, BrandSerializer, ImageSerializer, ProductSerializer, LikeSerializer,
    UserInfoSerializer, OrderSerializer, OrderItemSerializer, StatusOrderSerializer
)
import json
from .perms import UserInfoOwner


class UserViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    parser_classes = [parsers.MultiPartParser, ]

    def get_permissions(self):
        if self.action in ['current_user', 'change_password']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    @action(methods=['get', 'put'], detail=False, url_path='current-user')
    def current_user(self, request):
        u = request.user
        if request.method.__eq__('PUT'):
            for k, v in request.data.items():
                setattr(u, k, v)
            u.save()

        return Response(UserSerializer(u, context={'request': request}).data)

    @action(methods=['post'], detail=False, url_path='change-password')
    def change_password(self, request):
        user = request.user
        old_password = request.data['old_password']
        print(old_password)
        new_password = request.data['new_password']
        if user.check_password(old_password):
            return Response({"errors": "old_password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user.set_password(new_password)
            user.save()
            return Response(UserSerializer(user, context={'request': request}).data)


class ProductViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView, generics.UpdateAPIView,
                     generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = CustomPagination

    def list(self, request, *args, **kwargs):
        # Get the custom limit from the query parameter or use a default
        limit = int(request.query_params.get('limit', 100))
        # Retrieve the queryset
        queryset = self.filter_queryset(self.get_queryset())
        kw = request.query_params.get('kw')
        cateId = request.query_params.get('cateId')
        fromPrice = request.query_params.get('fromPrice')
        toPrice = request.query_params.get('toPrice')

        if kw:
            queryset = queryset.filter(name__contains=kw, description__contains=kw)
        if cateId:
            queryset = queryset.filter(category_id=cateId)
        if fromPrice and toPrice:
            queryset = queryset.filter(new_price__range=(fromPrice, toPrice))
        # if fromPrice = queryset.filter(category_id= )
        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response_data = self.get_paginated_response(serializer.data).data
            response_data['limit'] = limit  # Add the custom limit to the response
            return Response(response_data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class CategoryViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView, generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class BrandViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer


class ImageViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer


class LikeViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer


class UserInfoViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.RetrieveUpdateAPIView, ):
    queryset = UserInfo.objects.all()
    serializer_class = UserInfoSerializer
    permission_classes = [UserInfoOwner]

    @action(methods=['get'], detail=False)
    def current_info(self, request):
        user = request.user
        userinfo = UserInfo.objects.get(user_id=user)
        return Response(UserInfoSerializer(userinfo, context={'request': request}).data)


class OrderViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.RetrieveAPIView, ):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(methods=['post'], detail=False, url_path='create')
    def create_order(self, request):
        order_items_data = json.loads(request.data.get('order_items'))
        order_status_data = json.loads(request.data.get('order_status'))

        user = request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            # # Serialize and save the Order
            with transaction.atomic():
                order = Order.objects.create(user_id=user.id)

                for order_item in order_items_data:
                    order_item['order'] = order.id
                    OrderItem.objects.create(order_id=order.id, product_id=order_item['id'],
                                             quantity=order_item['quantity'])

                order_status_data['order'] = order.id
                order_status = StatusOrderSerializer(data=order_status_data)
                order_status.is_valid(raise_exception=True)
                order_status.save()
                # Create and save StatusOrder associated with the Order
                return Response(order.uuid, status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=False, url_path='payment')
    def getPaypalClient(self, request):
        data = {
            'client_id': 'AUf3F8kr7ESOkbT2yMPYGFsFkwMRKLYppdSojKSZwA05V_d22OM2175iiBDwLit777i22xY1wCs7BL0C',
            'client_secret': 'EHjvQszXeEKpu01L99u3gIhYr8SgYnBUjtxkEGI1Z5MLt3nEHNkkAkHRnvuzPT4vgPAK3k9Cogha1xuV'
        }
        return Response(data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False, url_path='get-receipt')
    def get_receipt(self, request):
        user = request.user
        uuid = json.loads(request.data.get('uuid'))
        order = Order.objects.filter(uuid=uuid).prefetch_related('order_item_order', 'status_order').first()
        order_data = OrderSerializer(order).data

        order_items = [items for items in order.order_item_order.all()]
        order_items_data = OrderItemSerializer(order_items, many=True, context={'request': request}).data

        status_order = [status_order for status_order in order.status_order.all()]
        status_order_data = StatusOrderSerializer(status_order[0]).data

        recepit = {'order': order_data, 'order_items': order_items_data, 'status': status_order_data}

        return HttpResponse(json.dumps(recepit), status=status.HTTP_200_OK)

    # if request.method.__eq__('GET'):
    #     user = request.user
    #     orders = Order.objects.filter(user_id=user.id)
    #     receipts = []
    #     for o in orders:
    #         o_serializer = OrderSerializer(o, context={'request': request})
    #         ord = o_serializer.data
    #         products = []
    #
    #         order_items = OrderItem.objects.filter(order_id=o.id)
    #         for data in order_items.values():
    #             p = Product.objects.get(pk=data['product_id'])
    #             prod = ProductSerializer(p, context={'request': request})
    #             data['product'] = prod.data
    #             products.append(data)
    #
    #         s = StatusOrder.objects.get(order_id=o.id)
    #         status_serializer = StatusOrderSerializer(s, context={'request': request})
    #         status_order = status_serializer.data
    #
    #         receipts.append({
    #             'order': ord,
    #             'order_items': products,
    #             'status': status_order
    #         })
    #     return Response(receipts, status=status.HTTP_200_OK)
    # else:
    #     uuid = request.data
    #     order = Order.objects.filter(uuid=uuid)
    #     products = []
    #     status_order = None
    #     if order.exists():
    #         order_instance = order.values()[0]
    #         order_items = OrderItem.objects.filter(order_id=order_instance['id'])
    #         for data in order_items.values():
    #             p = Product.objects.get(pk=data['product_id'])
    #             prod = ProductSerializer(p, context={'request': request})
    #             data['product'] = prod.data
    #             products.append(data)
    #         s = StatusOrder.objects.get(order_id=order_instance['id'])
    #         status_serializer = StatusOrderSerializer(s, context={'request': request})
    #         status_order = status_serializer.data
    #     receipt = {
    #         'order': order.values()[0],
    #         'order_items': products,
    #         'status': status_order
    #     }
    #     return Response(receipt, status=status.HTTP_200_OK)


class OrderItemViewSet(viewsets.ViewSet, generics.ListAPIView, generics.UpdateAPIView, generics.CreateAPIView,
                       generics.RetrieveAPIView, generics.RetrieveUpdateAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer


class StatusOrderViewSet(viewsets.ViewSet, generics.ListAPIView, generics.UpdateAPIView, generics.CreateAPIView,
                         generics.RetrieveAPIView, generics.RetrieveUpdateAPIView):
    queryset = StatusOrder.objects.all()
    serializer_class = StatusOrderSerializer
