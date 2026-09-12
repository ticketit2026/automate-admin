from django.urls import path

from . import views


urlpatterns = [

    path(
        '',
        views.letter_list,
        name='letter_list'
    ),

    path(
        'create/',
        views.letter_create,
        name='letter_create'
    ),

    path(
        '<int:letter_id>/',
        views.letter_detail,
        name='letter_detail'
    ),

    path(
        '<int:letter_id>/edit/',
        views.letter_edit,
        name='letter_edit'
    ),

    path(
        '<int:letter_id>/delete/',
        views.letter_delete,
        name='letter_delete'
    ),

    path(
        '<int:letter_id>/send/',
        views.letter_send,
        name='letter_send'
    ),

]
