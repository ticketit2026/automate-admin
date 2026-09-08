from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),   # اگر بخوای با Django auth
    # می‌تونی بعداً با allauth اضافه کنی
]