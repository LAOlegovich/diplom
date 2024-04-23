from django.test import TestCase
from django.urls import reverse

import pytest
from backend.models import User, Shop, Category, Product, Product_positions, Order

from rest_framework.test import APIClient


@pytest.fixture
def client():
    return APIClient()

@pytest.mark.django_db
def test_upload_catalog(client):

    user = User.objects.create(username='Isaak', password='12345', type='2', email = 'LwO6H@example.com')
  
    client.force_authenticate(user=user)

    data_ = {"url": "https://raw.githubusercontent.com/netology-code/pd-diplom/master/data/shop1.yaml"}
    responce = client.post(reverse('upload-catalog'), data= data_, format = 'json')

    print(reverse('upload-catalog'))
    
    assert responce.status_code == 200

    assert Shop.objects.count() != 0

@pytest.mark.django_db
def test_get_shops(client):

    user = User.objects.create(username='Isaak', password='12345', type='2', email = 'LwO6H@example.com')

    client.force_authenticate(user=user)

    Shop.objects.create(name = 'test', user = user)

    responce = client.get('/shops/', format = 'json')

    assert responce.status_code == 200

    data = responce.json()

    assert data[0]['name'] == 'test'


@pytest.mark.django_db
def test_patch_shops(client):

    user = User.objects.create(username='Isaak', password='12345', type='2', email = 'LwO6H@example.com')

    client.force_authenticate(user=user)

    shop = Shop.objects.create(name = 'test', user = user)

    data_ = {'name': 'test_2'}
    responce = client.patch(f'/shops/{shop.id}/', data= data_, format = 'json')

    assert responce.status_code == 200

    data = responce.json()

    assert Shop.objects.count() == 1

    assert Shop.objects.filter(name = 'test_2').count() == 1


@pytest.mark.django_db
def test_delete_shops(client):

    user = User.objects.create(username='Isaak', password='12345', type='2', email = 'LwO6H@example.com')

    client.force_authenticate(user=user)

    shop = Shop.objects.create(name = 'test', user = user)

    assert Shop.objects.count() == 1

    client.delete(f'/shops/{shop.id}/', format = 'json')

    assert Shop.objects.filter(name = 'test').count() == 0

@pytest.mark.django_db
def test_get_categories(client):

    user = User.objects.create(username='Isaak', password='12345', type='1', email = 'LwO6H@example.com')

    client.force_authenticate(user=user)

    Category.objects.create(name = 'TV')

    responce = client.get('/categories/', format = 'json')

    assert responce.status_code == 200

    data = responce.json()

    assert data[0]['name'] == 'TV'


@pytest.mark.django_db
def test_post_categories(client):

    user = User.objects.create(username='Isaak', password='12345', type='1', email = 'LwO6H@example.com')

    client.force_authenticate(user=user)

    data_ = {'name': 'telephone'}
    responce = client.post('/categories/', data= data_, format = 'json')

    assert responce.status_code == 201

    assert Category.objects.filter(name = 'telephone').count() == 1


@pytest.mark.django_db
def test_patch_categories(client):

    user = User.objects.create(username='Isaak', password='12345', type='1', email = 'LwO6H@example.com')

    client.force_authenticate(user=user)

    category = Category.objects.create(name = 'TV')

    data_ = {'name': 'telephoniese'}
    responce = client.patch(f'/categories/{category.id}/', data= data_, format = 'json')

    assert responce.status_code == 200

    assert Category.objects.filter(name = 'telephone').count() == 0

    assert Category.objects.filter(name = 'telephoniese').count() == 1


@pytest.mark.django_db
def test_delete_categories(client):

    user = User.objects.create(username='Isaak', password='12345', type='1', email = 'LwO6H@example.com')

    client.force_authenticate(user=user)

    category = Category.objects.create(name = 'TV')

    assert Category.objects.count() == 1

    client.delete(f'/categories/{category.id}/', format = 'json')

    assert Category.objects.filter(name = 'TV').count() == 0


@pytest.mark.django_db
def test_get_products(client):

    user = User.objects.create(username='Isaak', password='12345', type='1', email = 'LwO6H@example.com')

    client.force_authenticate(user=user)

    Product.objects.create(name = 'product_1', model = 'model_1', description = 'product number one', category = Category.objects.create(name = 'TV'))

    Product.objects.create(name = 'product_2', model = 'model_2', description = 'product number two', category = Category.objects.create(name = 'mobile'))

    shop_1 = Shop.objects.create(name = 'test', user = user, state =True)

    Product_positions.objects.create(product = Product.objects.get(name = 'product_1'), 
                                     price = 100, price_rrc = 200, quantity = 10, shop = shop_1)
    Product_positions.objects.create(product = Product.objects.get(name = 'product_2'), 
                                     price = 10, price_rrc = 45, quantity = 10, shop = shop_1)

    responce = client.get('/products/',{'product__name':'product_1'} ,format = 'json')

    assert responce.status_code == 200

    data = responce.json()
    print(data)

    assert data[0]['product'][0]['name'] == 'product_1'


@pytest.mark.django_db
def test_backet_get_and_post(client):

    user = User.objects.create(username='Isaak', password='12345', type='1', email = 'LwO6H@example.com')

    client.force_authenticate(user=user)
    product_1 = Product.objects.create(name = 'product_1', model = 'model_1', description = 'product number one', category = Category.objects.create(name = 'TV'))
    product_2 =Product.objects.create(name = 'product_2', model = 'model_2', description = 'product number two', category = Category.objects.create(name = 'mobile'))

    shop_1 = Shop.objects.create(name = 'MVideo', user = user, state = True)
    Product_positions.objects.create(product = Product.objects.get(name = 'product_1'), 
                                     price = 100, price_rrc = 200, quantity = 10, shop = shop_1)
    shop_2 = Shop.objects.create(name = 'MegaMarket', user = user, state = True)
    Product_positions.objects.create(product = Product.objects.get(name = 'product_2'), 
                                     price = 10, price_rrc = 45, quantity = 10, shop = shop_2)
    data_ =  {
    "items": [
	{"product_id":  product_1.id,	"quantity": 2},
	{"product_id":  product_2.id,	"quantity": 5}
    ]
    }
    responce = client.post('/basket/',data= data_, format = 'json')

    assert responce.status_code in (200,201)

    assert Order.objects.filter(user = user, status = 1).count() == 1

    responce = client.get('/basket/', format = 'json')

    assert responce.status_code == 200
    
    assert len(responce.json()) == 1

@pytest.mark.django_db
def test_basket_patch(client):

    user = User.objects.create(username='Isaak', password='12345', type='1', email = 'LwO6H@example.com')

    client.force_authenticate(user=user)
    product_1 = Product.objects.create(name = 'product_1', model = 'model_1', description = 'product number one', category = Category.objects.create(name = 'TV'))
    
    shop_1 = Shop.objects.create(name = 'MVideo', user = user, state = True)
    Product_positions.objects.create(product = Product.objects.get(name = 'product_1'), 
                                     price = 100, price_rrc = 200, quantity = 10, shop = shop_1)
    
   
    client.post('/basket/',{
        "items": [
	{"product_id":  product_1.id,	"quantity": 2},
    ]
    }, format = 'json')

    assert Order.objects.filter(user = user, status = 1,order_recs__quantity = 2).count() == 1

    client.patch('/basket/1/', {
        "items": [
	{"product_id":  product_1.id,	"quantity": 5},
    ]
    }, format = 'json')

    assert Order.objects.filter(user = user, status = 1,order_recs__quantity = 5).count() == 1

@pytest.mark.django_db
def test_basket_delete(client):

    user = User.objects.create(username='Isaak', password='12345', type='1', email = 'LwO6H@example.com')

    client.force_authenticate(user=user)
    product_1 = Product.objects.create(name = 'product_1', model = 'model_1', description = 'product number one', category = Category.objects.create(name = 'TV'))
    
    shop_1 = Shop.objects.create(name = 'MVideo', user = user, state = True)

    Product_positions.objects.create(product = Product.objects.get(name = 'product_1'), 
                                     price = 100, price_rrc = 200, quantity = 10, shop = shop_1)
    
    client.post('/basket/',{
        "items": [
	{"product_id":  product_1.id,	"quantity": 2},
    ]
    }, format = 'json')

    assert Order.objects.filter(user = user, status = 1,order_recs__quantity = 2).count() == 1

    responce = client.delete('/basket/', {'items':[product_1.id]},format = 'json')

    assert responce.json()['Deleted objects'] == 1
