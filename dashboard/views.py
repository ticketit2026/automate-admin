from django.shortcuts import render
from helpdesk.models import Ticket


def overview(request):
    tickets_count = Ticket.objects.count()

    return render(
        request,
        'dashboard/overview.html',
        {
            'tickets_count': tickets_count
        }
    )
