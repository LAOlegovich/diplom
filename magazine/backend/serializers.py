from .models import Order, Order_rec,Product,Product_positions, Shop,Category, User, Parameter, TYPE_OF_USER

import rest_framework

class UserSerializer(rest_framework.serializers.ModelSerializer):
    class Meta:
        model = User
        fields= ['first_name','last_name','email','type']

class CategorySerializer(rest_framework.serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name']

class ShopSerializer(rest_framework.serializers.ModelSerializer):
    user = UserSerializer(read_only = True)
    categories = CategorySerializer(many = True, read_only = True)
    class Meta:
        model = Shop
        fields = ['name','address','user','categories','state']


class ProductSerializer(rest_framework.serializers.ModelSerializer):
    category = CategorySerializer(read_only = True)
    class Meta:
        model = Product
        fields = ['name','model','description','category']


class ParameterSerializer(rest_framework.serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = ['name']


class Product_positionSerializer(rest_framework.serializers.ModelSerializer):
    product = ProductSerializer(read_only = True)
    shop = ShopSerializer(read_only = True)
    product_positions = ParameterSerializer(many = True, read_only = True)
    class Meta:
        model = Product_positions
        fields = ['product','shop','price','price_rrc','quantity','product_positions']


class OrderSerializer(rest_framework.serializers.ModelSerializer):
    user = UserSerializer(read_only = True)
    class Meta:
        model = Order
        fields =['id','time_order','status','user']
        read_only_fields= ('id','time_order',)

class Order_recSerializer(rest_framework.serializers.ModelSerializer):
    class Meta:
        model = Order_rec
        fields = ['id','quantity','product_position','order']
        read_only_fields= ('id',)