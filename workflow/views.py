from django.shortcuts import render
from .models import LeaveRequest, PurchaseRequest, MissionRequest

def workflow_dashboard(request):
    leaves = LeaveRequest.objects.all()
    purchases = PurchaseRequest.objects.all()
    missions = MissionRequest.objects.all()
    return render(request, 'workflow/dashboard.html', {
        'leaves': leaves,
        'purchases': purchases,
        'missions': missions
    })