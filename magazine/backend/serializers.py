from rest_framework.exceptions import ValidationError

from .models import Order, Order_rec,Product,Product_positions, Shop,Category, User, Parameter, Location_address,TYPE_OF_USER

import rest_framework

class UserSerializer(rest_framework.serializers.ModelSerializer):
    class Meta:
        model = User
        fields= ['username','first_name','last_name','email','type']

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

class Location_addressSerializer(rest_framework.serializers.ModelSerializer):
    user = UserSerializer(read_only = True)
    class Meta:
        model = Location_address
        fields = ['user','telephone', 'city','street','house','flat']

    def validate(self, data):
        """Метод для валидации. Вызывается при создании и обновлении."""
        _user_id = self.context["request"].user.id
        _user_type = self.context["request"].user.type
        Cnt = Location_address.objects.filter(user_id = _user_id).count()
 
        if Cnt >= 5 and _user_type == '1':
            raise   ValidationError("Превышен лимит на создание адресов покупателей")

        return data