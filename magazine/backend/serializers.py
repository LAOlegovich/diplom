from .models import Order, Order_rec,Product,Product_positions, Shop,Category, User, Parameter

import rest_framework

class UserSerializer(rest_framework.serializers.ModelSerializer):
    class Meta:
        model = User
        fields= ['firstname','lastname','email','type']

class CategorySerializer(rest_framework.serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name']

class ShopSerializer(rest_framework.serializers.ModelSerializer):
    user = UserSerializer(read_only = True)
    categories = CategorySerializer(many = True, read_only = True)
    class Meta:
        model = Shop
        fields = ['name','address','user','categories']


class ProductSerializer(rest_framework.serializers.ModelSerializer):
    category = CategorySerializer(real_only = True)
    class Meta:
        model = Product
        fields = ['name','description','category']


class ParameterSerializer(rest_framework.serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = ['name','value']


class Product_positionSerializer(rest_framework.serializers.ModelSerializer):
    product = ProductSerializer(read_only = True)
    shop = ShopSerializer(read_only = True)
    product_positions = ParameterSerializer(many = True, read_only = True)
    class Meta:
        model = Product_positions
        fields = ['product','shop','price','quantity','product_positions']


class OrderSerializer(rest_framework.serializers.ModelSerializer):
    class Meta:
        model = Order
        fields =[]

