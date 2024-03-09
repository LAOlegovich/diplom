from django.shortcuts import render
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request
from yaml import load as load_yaml, Loader
from django.http import JsonResponse
from requests import get

from .models import Order_rec, Order, Product, Product_positions, Shop, Category, Parameter, ProductParams

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


class UploadCatalog(APIView):

    def post(self,request, *args, **kwargs):
        URL = request.data.get('url')
        if URL:
            data = load_yaml(get(URL).content, Loader = Loader)
            print(data)
            shop_obj, _ = Shop.objects.get_or_create(name = data['shop'], user_id = request.user.id)
            for category in data['categories']:
                cat_obj, _ = Category.objects.get_or_create(id= category['id'], name = category['name'])
                cat_obj.shops.add(shop_obj.id)
                cat_obj.save()
            Product_positions.objects.filter(shop_id = shop_obj.id).delete()
            for el in data['goods']:
                prod_obj,_ = Product.objects.get_or_create(name = el['name'], category_id= el['category'])
                prod_pos_obj = Product_positions.objects.create(
                    product_id = prod_obj.id,
                    model = el['model'],
                    price = el['price'],
                    price_rrc = el['price_rrc'],
                    quantity = el['quaintity'],
                    shop_id = shop_obj.id
                )
            for name_,value_ in el['parameters'].items():
                param_obj, _ = Parameter.objects.get_or_create(name = name_)
                ProductParams.objects.create(product_position_id = prod_pos_obj.id,
                                             parameter_id = param_obj.id,
                                             value = value_
                                             )
            return JsonResponse({'Status': 'OK'})
        else:
            return JsonResponse({'Status':'Bad request', 'Error':'Не правильный файл'})









