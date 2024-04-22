from django.test import TestCase
from django.urls import reverse

import pytest
from backend.models import User, Shop, Category

from rest_framework.test import APIClient



@pytest.fixture
def client():
    return APIClient()

@pytest.mark.django_db
def test_upload_catalog(client):

    user = User.objects.create(username='Isaak', password='12345', type=2, email = 'LwO6H@example.com')
  
    client.force_authenticate(user=user)

    data_ = {"url": "https://raw.githubusercontent.com/netology-code/pd-diplom/master/data/shop1.yaml"}
    responce = client.post(reverse('upload-catalog'), data= data_, format = 'json')
    
    assert responce.status_code == 200

    assert Shop.objects.count() != 0

@pytest.mark.django_db
def test_get_shops(client):

    user = User.objects.create(username='Isaak', password='12345', type=2, email = 'LwO6H@example.com')

    client.force_authenticate(user=user)

    Shop.objects.create(name = 'test', user = user)

    responce = client.get('/shops/', format = 'json')

    assert responce.status_code == 200

    data = responce.json()

    assert data[0]['name'] == 'test'


@pytest.mark.django_db
def test_patch_shops(client):

    user = User.objects.create(username='Isaak', password='12345', type=2, email = 'LwO6H@example.com')

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

    user = User.objects.create(username='Isaak', password='12345', type=2, email = 'LwO6H@example.com')

    client.force_authenticate(user=user)

    shop = Shop.objects.create(name = 'test', user = user)

    assert Shop.objects.count() == 1

    client.delete(f'/shops/{shop.id}/', format = 'json')

    assert Shop.objects.filter(name = 'test').count() == 0

@pytest.mark.django_db
def test_get_categories(client):

    user = User.objects.create(username='Isaak', password='12345', type=1, email = 'LwO6H@example.com')

    client.force_authenticate(user=user)

    Category.objects.create(name = 'TV')

    responce = client.get('/categories/', format = 'json')

    assert responce.status_code == 200

    data = responce.json()

    assert data[0]['name'] == 'TV'


@pytest.mark.django_db
def test_post_categories(client):

    user = User.objects.create(username='Isaak', password='12345', type=1, email = 'LwO6H@example.com')

    client.force_authenticate(user=user)

    data_ = {'name': 'telephone'}
    responce = client.post('/categories/', data= data_, format = 'json')

    assert responce.status_code == 201

    assert Category.objects.filter(name = 'telephone').count() == 1


@pytest.mark.django_db
def test_patch_categories(client):

    user = User.objects.create(username='Isaak', password='12345', type=1, email = 'LwO6H@example.com')

    client.force_authenticate(user=user)

    category = Category.objects.create(name = 'TV')

    data_ = {'name': 'telephoniese'}
    responce = client.patch(f'/categories/{category.id}/', data= data_, format = 'json')

    assert responce.status_code == 200

    assert Category.objects.filter(name = 'telephone').count() == 0

    assert Category.objects.filter(name = 'telephoniese').count() == 1


@pytest.mark.django_db
def test_delete_categories(client):

    user = User.objects.create(username='Isaak', password='12345', type=1, email = 'LwO6H@example.com')

    client.force_authenticate(user=user)

    category = Category.objects.create(name = 'TV')

    assert Category.objects.count() == 1

    client.delete(f'/categories/{category.id}/', format = 'json')

    assert Category.objects.filter(name = 'TV').count() == 0