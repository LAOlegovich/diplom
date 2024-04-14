"""
URL configuration for magazine project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from django_rest_passwordreset.views import reset_password_confirm, reset_password_request_token

from backend.views import ShopView, CategoryView, UploadCatalog, RegisterAccount, ConfirmAccount,LoginAccount,Location_addressView, ProductInfoView, \
BasketView, DoOrders,ShopOrders

from rest_framework.routers import DefaultRouter
from django.urls import path, include

router = DefaultRouter()
router.register('user-addresses',Location_addressView, 'view-addresses')
router.register('shops', ShopView, 'view-shops')
router.register('categories', CategoryView, 'view-category'),
router.register('products', ProductInfoView, 'view-prod-info'),
router.register('basket',BasketView, 'view-basket'),
router.register('user/orders',DoOrders, 'view-orders'),
router.register('adminshops',ShopOrders,'admin-shop')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('user/register', RegisterAccount.as_view(), name = 'user-register'),
    path('user/register/confirm', ConfirmAccount.as_view(),name = 'user-register-confirm'),
    path('user/login', LoginAccount.as_view(), name='user-login'),
    path('user/password_reset',reset_password_request_token, name = 'password-reset'),
    path('user/password_reset/confirm', reset_password_confirm, name = 'password-reset-confirm')
]+ router.urls
