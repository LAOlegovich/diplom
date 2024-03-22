from rest_framework.exceptions import ValidationError

from .models import Order, Order_rec,Product,Product_positions, Shop,Category, User, Parameter, Location_address,ProductParams,TYPE_OF_USER

import rest_framework

class UserSerializer(rest_framework.serializers.ModelSerializer):

    def to_representation(self,obj):   
        rep= super(UserSerializer,self).to_representation(obj)  
        for t in TYPE_OF_USER:
            if t[0] == obj.type:
                rep['type'] = t[1]
                return rep
            else:
                rep['type'] = 'unknown'
                return rep
    class Meta:
        model = User
        fields= ['username','first_name','last_name','email']

class CategorySerializer(rest_framework.serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name','slug_name']
        extra_kwargs = {
            'name': {'validators': []}}

class ShopSerializer(rest_framework.serializers.ModelSerializer):
    user = UserSerializer(read_only = True)
    categories = CategorySerializer(many = True)

    def create(self, validated_data):
        """Метод для создания"""
        categories = validated_data.pop('categories')
        validated_data["user"] = self.context["request"].user
        #return super().create(validated_data)
        shop,_ = Shop.objects.get_or_create(**validated_data)
                                             
        for category in categories:
            name_ = category['name']
            slug_name_ = category.get("slug_name")
            categ,_ = Category.objects.get_or_create(name = name_,  slug_name = slug_name_)
            categ.shops.add(shop.id)
            categ.save()
                                                                                                                      
        return shop
    
    def update(self, instance, validated_data):
        # достаем связанные данные для других таблиц
        categories = validated_data.pop('categories')

        # обновляем склад по его параметрам
        shop = super().update(instance, validated_data)

        for category in categories:
            name_ = category['name']
            slug_name_ = category.get("slug_name")
           
            categ,_=Category.objects.update_or_create(name= name_, slug_name = slug_name_)
            categ.shops.add(shop.id)
            categ.save()
       
        return shop

    def validate(self, data):
        """Метод для валидации. Вызывается при создании и обновлении."""
        _user_type = self.context['request'].user.type
        if _user_type =='1':
            raise   ValidationError("Пользователь не имеет полномочий для настройки данного объекта!")

        return data

    class Meta:
        model = Shop
        fields = ['name','address','user','categories','state']
        extra_kwargs = {
            'name': {'validators': []}}


class ProductSerializer(rest_framework.serializers.ModelSerializer):
    category = CategorySerializer(read_only = True)
    class Meta:
        model = Product
        fields = ['name','model','description','category']

class ProductParamsSerializer(rest_framework.serializers.ModelSerializer):
    parameter = rest_framework.serializers.StringRelatedField()
    class Meta:
        model = ProductParams
        fields = ('parameter','value',)

class Product_positionSerializer(rest_framework.serializers.ModelSerializer):
    product = ProductSerializer(read_only = True)
    shop = ShopSerializer(read_only = True)
    product_params = ProductParamsSerializer(many = True,read_only = True)
    #params = ParameterSerializer(many = True, read_only = True)

    class Meta:
        model = Product_positions
        fields = ['product','shop','price','price_rrc','quantity','product_params']

    def to_representation(self,obj):   
        rep= super(Product_positionSerializer,self).to_representation(obj)  

        rep['shop'] = Shop.objects.filter(id=obj.shop_id).values_list('name', flat=True)
        rep['product'] = Product.objects.filter(id=obj.product_id).select_related("category").values('name', 'model','description',"category__name")
        return rep


class OrderSerializer(rest_framework.serializers.ModelSerializer):
    class Meta:
        model = Order
        fields =['id','time_order','status']
        read_only_fields= ('id','time_order',)

class Order_recSerializer(rest_framework.serializers.ModelSerializer):
    class Meta:
        model = Order_rec
        fields = ['id','quantity','product_position','order']
        read_only_fields= ('id',)

class Location_addressSerializer(rest_framework.serializers.ModelSerializer):
    user = UserSerializer(read_only = True)

    def to_representation(self,obj):   
        rep= super(Location_addressSerializer,self).to_representation(obj)  

        rep['user'] = ' '.join([el.first_name + ' '+ el.last_name for el in User.objects.filter(id=obj.user_id)])
        return rep
       
    
    class Meta:
        model = Location_address
        fields = ['user','telephone','city','street','house','flat']
        extra_kwargs = {
            'user': {'write_only': True}
        }
   

    def create(self, validated_data):
        """Метод для создания"""
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)

    def validate(self, data):
        """Метод для валидации. Вызывается при создании и обновлении."""
        _user_id = self.context['request'].user.id
        _user_type = self.context['request'].user.type
        Cnt = Location_address.objects.filter(user_id = _user_id).count()
 
        if Cnt >= 5 and _user_type == '1':
            raise   ValidationError("Превышен лимит на создание адресов покупателей")

        return data
    
