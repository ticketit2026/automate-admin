from django.shortcuts import render

from helpdesk.models import Ticket
from admin_automation.models import InternalLetter
from workflow.models import LeaveRequest, PurchaseRequest, MissionRequest
from meetings.models import Meeting


def overview(request):

    tickets_count = Ticket.objects.count()

    letters_count = InternalLetter.objects.count()

    pending_leaves = LeaveRequest.objects.filter(
        status='pending'
    ).count()

    pending_purchases = PurchaseRequest.objects.filter(
        status='pending'
    ).count()

    pending_missions = MissionRequest.objects.filter(
        status='pending'
    ).count()

    pending_requests = (
        pending_leaves
        + pending_purchases
        + pending_missions
    )

    meetings_count = Meeting.objects.count()

    context = {
        'tickets_count': tickets_count,
        'letters_count': letters_count,
        'pending_requests': pending_requests,
        'pending_leaves': pending_leaves,
        'pending_purchases': pending_purchases,
        'pending_missions': pending_missions,
        'meetings_count': meetings_count,
    }

    return render(
        request,
        'dashboard/overview.html',
        context
    )
