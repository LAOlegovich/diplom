from django.db import models

from django.contrib.auth.models import AbstractUser

TYPE_OF_USER = (
    ('1' , 'Обычный'),
    ('2' , 'Админ'),
    ('3' ,'Супервайзер'),)

class User(AbstractUser):
    REQUIRED_FIELDS = []
    type = models.CharField(max_length=1, choices= TYPE_OF_USER, verbose_name = 'Тип пользователя', default = '1')
    telephone = models.CharField(max_length=20)
    address = models.CharField(max_length=200)

    class Meta:
        verbose_name = "Пользователь"

class Category(models.Model):
    id = models.AutoField(primary_key= True)
    name = models.CharField(max_length = 40, unique = True)
    short_name = models.CharField(max_length = 15)

    class Meta:
        verbose_name = "Категория"

    def __str__(self):
        return self.name
    
class Shop(models.Model):
    id = models.AutoField(primary_key= True)
    name = models.CharField(max_length = 30, unique = True, verbose_name = "Название")
    address = models.TextField(verbose_name = "Адрес")
    URL = models.URLField(max_length = 256)
    file_path = models.CharField(max_length = 100)
    categories = models.ManyToManyField(Category, related_name = "shops")

    class Meta:
        verbose_name = "Магазин"
        ordering = ["name"]

    def __str__(self):
        return self.name
    

class Product(models.Model):
    id = models.AutoField(primary_key= True)
    name = models.CharField(max_length = 50, unique = True, verbose_name = "Наименование")
    description = models.TextField(max_length = 200)
    category = models.ForeignKey(Category, related_name = "products", on_delete = models.CASCADE)

    class Meta:
        verbose_name = "Продукт"
        ordering = ["name"]

    def __str__(self):
        return self.name
    

class Product_positions(models.Model):
    id = models.AutoField(primary_key= True)
    product = models.ForeignKey(Product, related_name = "prod_param",on_delete = models.CASCADE)
    shop = models.ForeignKey(Shop, related_name = "prod_pos_shop",on_delete = models.CASCADE)
    quantity = models.IntegerField()
    quantity_reserve = models.IntegerField()
    price = models.FloatField()
    
    class Meta:
        verbose_name = "Позиция продукта"

    def __str__(self):
        return f"{self.product.name} in {self.shop.name}"
    

class Parameter(models.Model):
    name = models.CharField(max_length = 30, unique = True, verbose_name = "Название")
    value = models.CharField(max_length = 30)
    product_params = models.ManyToManyField(Product_positions, related_name= "product_positions")

    class Meta:
        verbose_name ="Параметры продукции"

    def __str__(self):
        return self.name
    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "order")
    status = models.CharField(max_length = 20)
    prod_position = models.ManyToManyField("Product_positions", through= "Order_rec")

    class Meta:
        verbose_name = "Корзина заказа"


STAT_OF_ORDER = (
    ('1' , 'Предзаказ'),
    ('2' , 'Оформлено'),
    ('3' , 'Обработано'),
)

class Order_rec(models.Model):
    product_position = models.ForeignKey(Product_positions, related_name = "product_record",on_delete = models.CASCADE)
    order = models.ForeignKey(Order, related_name = "order_recs", on_delete = models.CASCADE)
    status = models.CharField(max_length=1, choices=STAT_OF_ORDER, verbose_name = 'Статус заказа',default = '1')

    class Meta:
        verbose_name = "Позиция заказа"


   
    