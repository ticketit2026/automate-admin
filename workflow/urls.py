from django.urls import path
from . import views

urlpatterns = [
    path('', views.workflow_dashboard, name='workflow_dashboard'),
]