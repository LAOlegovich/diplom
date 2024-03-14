from decimal import Decimal
from django.db import models

from django.contrib.auth.models import AbstractUser

from django.core.validators import MinValueValidator

from django_rest_passwordreset.tokens import get_token_generator
from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """
    Миксин для управления пользователями
    """
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

TYPE_OF_USER = (
    ('1' , 'Покупатель'),
    ('2' , 'Продавец'),
    ('3' ,'Администратор_площадки'),)

class User(AbstractUser):
    REQUIRED_FIELDS = []
    objects = UserManager()
    USERNAME_FIELD = 'email'
    email = models.EmailField(('email address'), unique=True)
    type = models.CharField(max_length=1, choices= TYPE_OF_USER, verbose_name = 'Тип пользователя', default = '1')
    is_active = models.BooleanField(
        ('active'),
        default=False,
        help_text=(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    class Meta:
        verbose_name = "Пользователь"

class Category(models.Model):
    id = models.AutoField(primary_key= True)
    name = models.CharField(max_length = 40, unique = True)
    slug_name = models.SlugField(max_length = 20, null = True)

    class Meta:
        verbose_name = "Категория"

    def __str__(self):
        return self.name
    
class Shop(models.Model):
    id = models.AutoField(primary_key= True)
    name = models.CharField(max_length = 30, unique = True, verbose_name = "Название")
    address = models.TextField(verbose_name = "Адрес")
    URL = models.URLField(max_length = 256, null = True)
    file_path = models.CharField(max_length = 100, null = True)
    user = models.ForeignKey(User, related_name = "shops", on_delete = models.CASCADE)
    categories = models.ManyToManyField(Category, related_name = "shops")
    state = models.BooleanField(default = False, verbose_name = "статус получения товара")

    class Meta:
        verbose_name = "Магазин"
        ordering = ["name"]

    def __str__(self):
        return self.name
    

class Product(models.Model):
    id = models.AutoField(primary_key= True)
    name = models.CharField(max_length = 50, unique = True, verbose_name = "Наименование")
    model = models.CharField(max_length = 30, null = True)
    description = models.TextField(max_length = 200, null = True)
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
    quantity = models.PositiveIntegerField(null = False)
    quantity_reserve = models.PositiveIntegerField(null = False, default = 0)
    price = models.FloatField(validators = [MinValueValidator(Decimal('0.0'))])
    price_rrc = models.FloatField(validators = [MinValueValidator(Decimal('0.0'))])
    params = models.ManyToManyField("Parameter", through= "ProductParams")
    
    class Meta:
        verbose_name = "Позиция продукта"

    def __str__(self):
        return f"{self.product.name} in {self.shop.name}"
    

class Parameter(models.Model):
    id = models.AutoField(primary_key= True)
    name = models.CharField(max_length = 30, unique = True, verbose_name = "Название")


    class Meta:
        verbose_name ="Параметры продукции"

    def __str__(self):
        return self.name


class ProductParams(models.Model):
    product_position = models.ForeignKey(Product_positions, verbose_name = "инфа о позиции продукции",
                                         related_name = "product_params", 
                                         on_delete = models.CASCADE
                                         )
    parameter = models.ForeignKey(Parameter, verbose_name = "Параметр",
                                  related_name = "product_params",
                                  on_delete = models.CASCADE
                                  )
    value = models.CharField(max_length =50, verbose_name = "Значение параметра")

    class Meta:
        verbose_name = "Параметр"
        constraints = [models.UniqueConstraint(fields = ['product_position','parameter'],
                                               name = 'unic_prod_param')]

STAT_OF_ORDER = (
    ('1' , 'Предзаказ'),
    ('2' , 'Оформлено'),
    ('3' , 'Обработано'),
)  

class Order(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "order")
    prod_position = models.ManyToManyField("Product_positions", through= "Order_rec")
    time_order = models.DateTimeField(auto_now_add = True)
    status = models.CharField(max_length=1, choices=STAT_OF_ORDER, verbose_name = 'Статус заказа',default = '1')

    class Meta:
        verbose_name = "Корзина заказа"




class Order_rec(models.Model):
    product_position = models.ForeignKey(Product_positions, related_name = "product_record",on_delete = models.CASCADE)
    order = models.ForeignKey(Order, related_name = "order_recs", on_delete = models.CASCADE)
    quantity = models.PositiveIntegerField(null = False)

    class Meta:
        verbose_name = "Позиция заказа"

class Location_address(models.Model):
    user = models.ForeignKey(User, verbose_name = "user", related_name = "users_addresses", on_delete = models.CASCADE)
    telephone = models.CharField(max_length=20)
    city = models.CharField(max_length=40, blank = True)
    street = models.CharField(max_length= 50, blank = True)
    house = models.CharField(max_length = 10, blank = True)
    flat = models.PositiveSmallIntegerField(blank = True)

    class Meta:
        verbose_name = "Адрес местонахождения пользователя"

    def __str__(self):
        return f'Users concact telephone is {self.telephone}'


class ConfirmEmailToken(models.Model):
    objects = models.manager.Manager()
    class Meta:
        verbose_name = 'Токен подтверждения Email'
        verbose_name_plural = 'Токены подтверждения Email'

    @staticmethod
    def generate_key():
        """ generates a pseudo random code using os.urandom and binascii.hexlify """
        return get_token_generator().generate_token()

    user = models.ForeignKey(
        User,
        related_name='confirm_email_tokens',
        on_delete=models.CASCADE     
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    # Key field, though it is not the primary key of the model
    key = models.CharField(
        max_length=64,
        db_index=True,
        unique=True
    )

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(ConfirmEmailToken, self).save(*args, **kwargs)

    def __str__(self):
        return "Password reset token for user {user}".format(user=self.user)
   
    
