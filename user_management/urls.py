from django.urls import path

from . import views


urlpatterns = [

    path(
        '',
        views.user_list,
        name='user_management'
    ),

    path(
        'create/',
        views.user_create,
        name='user_create'
    ),

    path(
        'edit/<int:user_id>/',
        views.user_edit,
        name='user_edit'
    ),

    path(
        'password/<int:user_id>/',
        views.user_password,
        name='user_password'
    ),

    path(
        'permissions/<int:user_id>/',
        views.user_permissions,
        name='user_permissions'
    ),

]
