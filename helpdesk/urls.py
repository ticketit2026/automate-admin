from django.urls import path
from . import views


urlpatterns = [

    # لیست تیکت‌ها و ثبت تیکت جدید
    path(
        '',
        views.ticket_list,
        name='ticket_list'
    ),

    # جزئیات تیکت
    path(
        '<int:ticket_id>/',
        views.ticket_detail,
        name='ticket_detail'
    ),

    # ویرایش تیکت
    path(
        '<int:ticket_id>/edit/',
        views.edit_ticket,
        name='edit_ticket'
    ),

    # حذف تیکت
    path(
        '<int:ticket_id>/delete/',
        views.delete_ticket,
        name='delete_ticket'
    ),

    # ثبت پاسخ
    path(
        '<int:ticket_id>/reply/',
        views.add_ticket_reply,
        name='add_ticket_reply'
    ),

    # تغییر وضعیت
    path(
        '<int:ticket_id>/status/',
        views.update_ticket_status,
        name='update_ticket_status'
    ),

    # ارجاع به کارشناس
    path(
        '<int:ticket_id>/assign/',
        views.assign_ticket,
        name='assign_ticket'
    ),
]
