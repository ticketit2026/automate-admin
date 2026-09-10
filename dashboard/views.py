from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from helpdesk.models import Ticket


@login_required
def overview(request):

    tickets_count = Ticket.objects.count()

    return render(
        request,
        'dashboard/overview.html',
        {
            'tickets_count': tickets_count
        }
    )
