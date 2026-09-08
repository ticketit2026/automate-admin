from django.contrib import admin
from .models import LeaveRequest, PurchaseRequest, MissionRequest

@admin.register(LeaveRequest)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ('employee', 'status', 'created_at')
    list_filter = ('status',)

@admin.register(PurchaseRequest)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('employee', 'item', 'status')
    list_filter = ('status',)

@admin.register(MissionRequest)
class MissionAdmin(admin.ModelAdmin):
    list_display = ('employee', 'destination', 'status')
    list_filter = ('status',)