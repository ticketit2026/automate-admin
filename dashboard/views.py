from django.shortcuts import render
from helpdesk.models import Ticket
from admin_automation.models import InternalLetter
from workflow.models import LeaveRequest, PurchaseRequest, MissionRequest
from meetings.models import Meeting
from documents.models import Document

def overview(request):
    context = {
        'tickets': Ticket.objects.count(),
        'letters': InternalLetter.objects.count(),
        'leaves': LeaveRequest.objects.filter(status='pending').count(),
        'purchases': PurchaseRequest.objects.filter(status='pending').count(),
        'missions': MissionRequest.objects.filter(status='pending').count(),
        'meetings': Meeting.objects.count(),
        'documents': Document.objects.count(),
    }
    return render(request, 'dashboard/overview.html', context)