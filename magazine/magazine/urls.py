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

from backend.views import ShopView, CategoryView, UploadCatalog, RegisterAccount, ConfirmAccount,LoginAccount,Location_addressView

from rest_framework.routers import DefaultRouter
from django.urls import path, include

router = DefaultRouter()
router.register('user-addresses',Location_addressView)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('categories', CategoryView.as_view(), name = 'view-categories'),
    path('shops', ShopView.as_view(), name = 'view-shops'),
    path('updatecatalog', UploadCatalog.as_view(), name = 'upload-catalog'),
    path('user/register', RegisterAccount.as_view(), name = 'register-user'),
    path('user/register/confirm', ConfirmAccount.as_view(),name = 'confirmation-account'),
    path('user/login', LoginAccount.as_view(), name='user-login')
]+ router.urls
