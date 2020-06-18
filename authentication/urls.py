from django.contrib import admin
from django.urls import path, include
from .views import UserViewSet,  index, app

urlpatterns = [
    path('users', UserViewSet),
    path('', index),
    path('uploaded', app),
]