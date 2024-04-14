from celery import shared_task

from backend.models import Shop, Category, Product, Parameter, Product_positions, ProductParams, User, ConfirmEmailToken
from django.conf import settings
from django.core.mail import EmailMultiAlternatives


@shared_task
def update_catalog(data,user_id):

    shop_obj, _ = Shop.objects.get_or_create(name = data['shop'], user_id = user_id)
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
            return 

@shared_task
def send_email_new_user(user_id):
    user = User.objects.get(id=user_id)
    token, _ = ConfirmEmailToken.objects.get_or_create(user_id=user.pk)

    msg = EmailMultiAlternatives(
        # title:
        f"Password Reset Token for {user.email}",
        # message:
        token.key,
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [user.email]
    )
    msg.send()
  