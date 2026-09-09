from django.contrib import admin

from .models import Ticket, TicketReply


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'status',
        'priority',
        'created_by',
        'assigned_to',
        'created_at',
        'updated_at',
    )

    list_filter = (
        'status',
        'priority',
        'assigned_to',
    )

    search_fields = (
        'title',
        'description',
        'created_by__username',
        'assigned_to__username',
    )


@admin.register(TicketReply)
class TicketReplyAdmin(admin.ModelAdmin):

    list_display = (
        'ticket',
        'user',
        'created_at',
    )

    search_fields = (
        'message',
        'user__username',
        'ticket__title',
    )

    list_filter = (
        'created_at',
    )
