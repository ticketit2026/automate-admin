from django.contrib import admin

from .models import InternalLetter


@admin.register(InternalLetter)
class InternalLetterAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'document_type',
        'status',
        'sent_to',
        'assigned_to',
        'created_by',
        'created_at',
    )

    list_filter = (
        'document_type',
        'status',
        'created_at',
    )

    search_fields = (
        'title',
        'content',
        'sent_to',
        'created_by__username',
        'assigned_to__username',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )
