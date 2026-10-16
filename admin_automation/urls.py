
from django.urls import path

from . import views
from .annotation_views import letter_annotate


urlpatterns = [
    path(
        "",
        views.letter_list,
        name="letter_list",
    ),

    path(
        "create/",
        views.letter_create,
        name="letter_create",
    ),

    path(
        "<int:letter_id>/",
        views.letter_detail,
        name="letter_detail",
    ),

    path(
        "<int:letter_id>/edit/",
        views.letter_edit,
        name="letter_edit",
    ),

    path(
        "<int:letter_id>/delete/",
        views.letter_delete,
        name="letter_delete",
    ),

    path(
        "<int:letter_id>/assign/",
        views.letter_assign,
        name="letter_assign",
    ),

    path(
        "<int:letter_id>/approve/",
        views.letter_approve,
        name="letter_approve",
    ),

    path(
        "<int:letter_id>/reject/",
        views.letter_reject,
        name="letter_reject",
    ),

    path(
        "<int:letter_id>/annotate/",
        letter_annotate,
        name="letter_annotate",
    ),
]
