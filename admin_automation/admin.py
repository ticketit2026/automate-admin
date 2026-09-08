from django.contrib import admin
from .models import InternalLetter

@admin.register(InternalLetter)
class InternalLetterAdmin(admin.ModelAdmin):
    list_display = ('title', 'document_type', 'status', 'sent_to', 'created_by')
    list_filter = ('document_type', 'status')
    search_fields = ('title', 'content')