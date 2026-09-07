from django.urls import path
from . import views

urlpatterns = [
    path('', views.letter_list, name='letter_list'),
]