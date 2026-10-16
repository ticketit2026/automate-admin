
from django.urls import path
from . import views

from .annotation_views import (
    letter_annotate,
    letter_annotation_page,
)

from .attachment_views import (
    letter_attachments,
    letter_attachment_download,
    letter_original_file_download,
    letter_attachment_edit,
    letter_attachment_delete,
)


urlpatterns = [
    # نامه‌های اداری
    path("", views.letter_list, name="letter_list"),
    path("create/", views.letter_create, name="letter_create"),
    path("<int:letter_id>/", views.letter_detail, name="letter_detail"),
    path("<int:letter_id>/edit/", views.letter_edit, name="letter_edit"),
    path("<int:letter_id>/delete/", views.letter_delete, name="letter_delete"),

    # ارجاع، تأیید و رد نامه
    path("<int:letter_id>/assign/", views.letter_assign, name="letter_assign"),
    path("<int:letter_id>/approve/", views.letter_approve, name="letter_approve"),
    path("<int:letter_id>/reject/", views.letter_reject, name="letter_reject"),

    # حاشیه‌نویسی نامه
    path(
        "<int:letter_id>/annotate/",
        letter_annotate,
        name="letter_annotate",
    ),
    path(
        "<int:letter_id>/annotate/page/<int:page_number>/",
        letter_annotation_page,
        name="letter_annotation_page",
    ),

    # مدیریت پیوست‌های نامه
    path(
        "<int:letter_id>/attachments/",
        letter_attachments,
        name="letter_attachments",
    ),
    path(
        "attachments/<int:attachment_id>/edit/",
        letter_attachment_edit,
        name="letter_attachment_edit",
    ),
    path(
        "attachments/<int:attachment_id>/delete/",
        letter_attachment_delete,
        name="letter_attachment_delete",
    ),
    path(
        "attachments/<int:attachment_id>/download/",
        letter_attachment_download,
        name="letter_attachment_download",
    ),

    # فایل اصلی نامه
    path(
        "<int:letter_id>/original-file/",
        letter_original_file_download,
        name="letter_original_file_download",
    ),
]
