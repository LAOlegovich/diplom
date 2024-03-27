from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import MethodNotAllowed
from yaml import load as load_yaml, Loader
from django.http import JsonResponse
from requests import get
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from backend.signals import new_user_registered, new_order
from .models import Order_rec, Order, Product, Product_positions, Shop, Category, Parameter, ProductParams, ConfirmEmailToken, Location_address,STAT_OF_ORDER

from .serializers import OrderSerializer, Product_positionSerializer, ShopSerializer, CategorySerializer,UserSerializer,\
    Location_addressSerializer

from rest_framework.permissions import IsAuthenticated

from .permissions import IsOwnerOrAdmin
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, F, Sum
from rest_framework.exceptions import ValidationError

# Create your views here.

class ShopView(ModelViewSet):
    """
    Класс для просмотра списка магазинов
    """
    serializer_class = ShopSerializer
    permission_classes = [IsOwnerOrAdmin, IsAuthenticated]

    def get_queryset(self):
        if self.request.user.type =='3':
            return Shop.objects.all()
        else:
            return  Shop.objects.filter(user_id = self.request.user.id)


class CategoryView(ModelViewSet):
    """ Класс для просмотра списка категорий"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


class UploadCatalog(APIView):
    """ Обновление каталога магазина"""
#Необходимо понимать, что обновлять каталог магазина может только администратор или владелец записи магазина,
  #  иначе получается анархия, еже ли магазина до этого на площадке не было, то welcome!
    def post(self,request, *args, **kwargs):
        URL = request.data.get('url')
        if URL:
            data = load_yaml(get(URL).content, Loader = Loader)

            id_user = Shop.objects.filter(name = data['shop']).values_list('user_id', flat=True)
#как раз то самое условие, про которое написано выше, 3 тип -администратор площадки.
            if request.user.type == 1 or request.user.type == 2 and request.user.id != id_user and id_user.first() is not None:
                return JsonResponse({'Status':'Bad request', 
                                     'Error':'User has no rights'})
            shop_obj, _ = Shop.objects.get_or_create(name = data['shop'], user_id = request.user.id)
            for category in data['categories']:
                cat_obj, _ = Category.objects.get_or_create(name = category['name']) #id= category['id'] 
                cat_obj.shops.add(shop_obj.id)
                cat_obj.save()
            Product_positions.objects.filter(shop_id = shop_obj.id).delete()
            for el in data['goods']:
                prod_obj,_ = Product.objects.get_or_create(name = el['name'], category_id= el['category'],model = el['model'])
                prod_pos_obj = Product_positions.objects.create(
                    product_id = prod_obj.id,
                    price = el['price'],
                    price_rrc = el['price_rrc'],
                    quantity = el['quantity'],
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
            return JsonResponse({'Status':'Bad request', 'Error':'Incorrect structure of file'})




class RegisterAccount(APIView):
    """
    Для регистрации покупателей
    """

    # Регистрация методом POST

    def post(self, request, *args, **kwargs):
        """
            Process a POST request and create a new user.

            Args:
                request (Request): The Django request object.

            Returns:
                JsonResponse: The response indicating the status of the operation and any errors.
            """
        # проверяем обязательные аргументы
        if {'first_name', 'last_name', 'email', 'password'}.issubset(request.data):

            # проверяем пароль на сложность
            try:
                validate_password(request.data['password'])
            except Exception as password_error:
                error_array = []
                # noinspection PyTypeChecker
                for item in password_error:
                    error_array.append(item)
                return JsonResponse({'Status': False, 'Errors': {'password': error_array}})
            else:
                # проверяем данные для уникальности имени пользователя

                user_serializer = UserSerializer(data=request.data)
                if user_serializer.is_valid():
                    # сохраняем пользователя
                    user = user_serializer.save()
                    user.set_password(request.data['password'])
                    user.save()
                    return JsonResponse({'Status': True})
                else:
                    return JsonResponse({'Status': False, 'Errors': user_serializer.errors})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class ConfirmAccount(APIView):
    """
    Класс для подтверждения почтового адреса
    """

    # Регистрация методом POST
    def post(self, request, *args, **kwargs):
        """
                Подтверждает почтовый адрес пользователя.

                Args:
                - request (Request): The Django request object.

                Returns:
                - JsonResponse: The response indicating the status of the operation and any errors.
                """
        # проверяем обязательные аргументы
        if {'email', 'token'}.issubset(request.data):

            token = ConfirmEmailToken.objects.filter(user__email=request.data['email'],
                                                     key=request.data['token']).first()
            if token:
                token.user.is_active = True
                token.user.save()
                token.delete()
                return JsonResponse({'Status': True})
            else:
                return JsonResponse({'Status': False, 'Errors': 'Incorrect token or email'})

        return JsonResponse({'Status': False, 'Errors': 'No all needed arguments'})



class LoginAccount(APIView):
    """
    Класс для авторизации пользователей
    """

    # Авторизация методом POST
    def post(self, request, *args, **kwargs):
        """
                Authenticate a user.

                Args:
                    request (Request): The Django request object.

                Returns:
                    JsonResponse: The response indicating the status of the operation and any errors.
                """
        if {'email', 'password'}.issubset(request.data):
            user = authenticate(request, username=request.data['email'], password=request.data['password'])

            if user is not None:
                if user.is_active:
                    token, _ = Token.objects.get_or_create(user=user)

                    return JsonResponse({'Status': True, 'Token': token.key})

            return JsonResponse({'Status': False, 'Errors': 'Not authorize'})


class Location_addressView(ModelViewSet):
    """ 
        Вьюсет для управления адресами пользователей,
        обновление адреса заблокировано - делать через два действия: удаления и создания вновь
    """

    serializer_class = Location_addressSerializer
    permission_classes = [IsOwnerOrAdmin, IsAuthenticated]

    def get_queryset(self):
        if self.request.user.type =='3':
            return Location_address.objects.all()
        else:
            return  Location_address.objects.filter(user_id = self.request.user.id)

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed('PATCH,PUT')



class ProductInfoView(ModelViewSet):

    serializer_class = Product_positionSerializer
    filter_backends = [DjangoFilterBackend]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        query = Q(shop__state=True)
        filter_fields = ['price','price_rrc','quantity','shop__name','product__category__name', 'product__name','product_params__value','product_params__parameter__name']

        for param in self.request.GET:

            if param in filter_fields:
                param_values = self.request.query_params.get(param)
                kw = {param: param_values}
                query = query & Q(**kw)
            else:
                raise ValidationError(f'Invalid using Filter Fields, you can use this fields:{filter_fields}')

        return Product_positions.objects.filter(query).select_related("shop","product")\
        .prefetch_related("product_params__parameter").distinct()


class BasketView(ModelViewSet):
    """ Класс для работы с корзиной пользователя"""
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        vals = Order.objects.filter(user_id = self.request.user.id, status = '1').prefetch_related("order_recs","order_recs__product_position").\
        annotate(total_sum=Sum(F('order_recs__quantity') * F('order_recs__product_position__price'))).distinct()
        if vals.count() != 0:
            return vals
        else:
            res = ValidationError("Корзина пуста!")
            res.status_code = status.HTTP_204_NO_CONTENT
            raise res

    def create(self,request):
        if self.request.user.__getattribute__('type') != '1':

            raise  ValidationError("Только под учетной записью клиента магазина можно работать с корзиной!")
        
        else:
            items_list = request.data.get('items')
            basket, _ = Order.objects.get_or_create(user_id=request.user.id, status='1')
            objects_created = 0
            for item in items_list:
                _,created = Order_rec.objects.get_or_create(product_position_id = item.get('product_id'), \
                                                   defaults= {"order_id":basket.id, "product_position_id":item.get('product_id'),\
                                                            "quantity": item.get('quantity')})
   
                objects_created += created

                    
            return JsonResponse({'Status': True, 'Create objects': objects_created})
        
    def update(self,request, *args, **kwargs):
        if self.request.user.__getattribute__('type') != '1':

            raise  ValidationError("Только под учетной записью клиента магазина можно работать с корзиной!")
        else:
            items_list = request.data.get('items')
            basket, _ = Order.objects.get_or_create(user_id=request.user.id, status='1')
            objects_updated = 0
            for item in items_list:
                _, updated = Order_rec.objects.update_or_create(product_position_id = item.get('product_id'), order_id=basket.id, \
                                                   defaults= {"quantity": item.get('quantity')})
   
                objects_updated += updated

            return JsonResponse({'Status': True, 'Objects updated': objects_updated})
        
    def delete(self,request,*args, **kwargs):
        if self.request.user.__getattribute__('type') != '1':

            raise  ValidationError("Только под учетной записью клиента магазина можно работать с корзиной!")
        else:
            items_list = request.data.get('items')
            objects_deleted = 0
            for item in items_list:
                objects_deleted+= Order_rec.objects.prefetch_related('order_recs').\
                    filter(product_position_id = item, order__user_id = self.request.user.id, order__status ='1').delete()[0]

        return JsonResponse({'Status': True, 'Deleted objects': objects_deleted})

class DoOrders(ModelViewSet):
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        vals = Order.objects.exclude(status = '1').filter(user_id = self.request.user.id).prefetch_related("prod_position").\
            annotate(total_sum=Sum(F('order_recs__quantity') * F('order_recs__product_position__price'))).distinct()
        if vals.count() != 0:
            return vals
        else:
            res = ValidationError("Активных заказов нет!")
            res.status_code = status.HTTP_204_NO_CONTENT
            raise res
        
    def create(self,request,*args,**kwargs):
        if self.request.user.__getattribute__('type') != '1':
            raise  ValidationError("Только под учетной записью клиента магазина можно работать с корзиной!")
        elif {'order_id','loc_address_id'}.issubset(request.data):
            rec_id = Order.objects.prefetch_related("prod_position").\
                filter(user_id = request.user.id, id = request.data.get('order_id'), status = '1'). \
                        update(status="2", loc_address_id= request.data.get('loc_address_id'))

            if rec_id:
                # for pos_id in Order_rec.objects.filter(order_id = request.data.get('order_id')).values_list('product_position_id', flat =True):
                #     quantity = Order_rec.objects.filter(product_position_id = pos_id).values_list('quantity', flat= True)
                #     Product_positions.objects.filter(id = pos_id).update(quantity_reserve = F('quantity_reserve')+quantity)
                dict = {'status':"Новый", "order_id":request.data.get('order_id')}
                new_order.send(sender=self.__class__, user_id=request.user.id, **dict)

            return JsonResponse({'Status': True, "Updated":rec_id})
        else:
            return JsonResponse({'Status': False, 'Errors': 'Not all needed arguments'})



        
class ShopOrders(ModelViewSet):
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.__getattribute__('type') != '2':
            raise  ValidationError("Получение заказов доступно только для учетных записей продавцов!")
        else:
            return Order.objects.filter(order_recs__product_position__shop__user_id = self.request.user.id).exclude(status = '1').\
            prefetch_related('order_recs__product_position__params',
            'order_recs__product_position__product__category').select_related('loc_address').annotate(
                total_sum=Sum(F('order_recs__quantity') * F('order_recs__product_position__price'))
            ).distinct()
        
    def create(self, request, *args, **kwargs):
            raise MethodNotAllowed('POST')
    
    def delete(self,request):
        raise MethodNotAllowed('DELETE')


    def update(self, request, *args, **kwargs):
        if self.request.user.__getattribute__('type') != '2':
            raise  ValidationError("Получение заказов доступно только для учетных записей продавцов!")
        else:
            if request.data.get('status') == 1:
                raise ValidationError("Невозможна установка статуса Корзина")
            Order.objects.filter(id = request.data.get('order_id'), order_recs__product_position__shop__user_id = self.request.user.id).\
                exclude(status ='1').update(status = request.data.get('status'))
            dict = {'status':(val[1] for val in STAT_OF_ORDER if request.data.get('status')== int(val[0])),
                    "order_id":request.data.get('order_id')}
            new_order.send(sender=self.__class__, user_id=request.user.id, **dict)
            
            return super().update(request, *args, **kwargs)


    
