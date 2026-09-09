from django.urls import path
from . import views


urlpatterns = [

    path(
        '',
        views.ticket_list,
        name='ticket_list'
    ),

    path(
        '<int:ticket_id>/',
        views.ticket_detail,
        name='ticket_detail'
    ),

    path(
        '<int:ticket_id>/status/',
        views.update_ticket_status,
        name='update_ticket_status'
    ),

    path(
        '<int:ticket_id>/assign/',
        views.assign_ticket,
        name='assign_ticket'
    ),

]
