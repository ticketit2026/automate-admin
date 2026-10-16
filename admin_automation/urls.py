```python
from django.urls import path
from . import views
from .annotation_views import letter_annotate, letter_annotation_page
from .attachment_views import letter_attachments, letter_attachment_download

urlpatterns = [
    # فهرست نامه‌ها
    path("", views.letter_list, name="letter_list"),

    # ایجاد نامه
    path("create/", views.letter_create, name="letter_create"),

    # جزئیات نامه
    path("<int:letter_id>/", views.letter_detail, name="letter_detail"),

    # ویرایش نامه
    path("<int:letter_id>/edit/", views.letter_edit, name="letter_edit"),

    # حذف نامه
    path("<int:letter_id>/delete/", views.letter_delete, name="letter_delete"),

    # ارجاع نامه
    path("<int:letter_id>/assign/", views.letter_assign, name="letter_assign"),

    # تأیید نامه
    path("<int:letter_id>/approve/", views.letter_approve, name="letter_approve"),

    # رد نامه
    path("<int:letter_id>/reject/", views.letter_reject, name="letter_reject"),

    # حاشیه‌نویسی نامه
    path(
        "<int:letter_id>/annotate/",
        letter_annotate,
        name="letter_annotate",
    ),

    # نمایش تصویر هر صفحه برای حاشیه‌نویسی
    path(
        "<int:letter_id>/annotate/page/<int:page_number>/",
        letter_annotation_page,
        name="letter_annotation_page",
    ),

    # مدیریت پیوست‌های اسکن‌شده و امضاشده
    path(
        "<int:letter_id>/attachments/",
        letter_attachments,
        name="letter_attachments",
    ),

    # مشاهده یا دانلود امن پیوست
    path(
        "attachments/<int:attachment_id>/download/",
        letter_attachment_download,
        name="letter_attachment_download",
    ),
]
```
