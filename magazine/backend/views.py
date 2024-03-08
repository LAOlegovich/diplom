from django.shortcuts import render
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Order_rec, Order, Product, Product_positions, Shop, Category

from .serializers import Order_recSerializer, OrderSerializer, ProductSerializer, Product_positionSerializer, ShopSerializer, CategorySerializer

# Create your views here.

class ShopView(ListAPIView):
    """
    Класс для просмотра списка магазинов
    """
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer


class CategoryView(ListAPIView):
    """ Класс для просмотра списка категорий"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

