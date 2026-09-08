from django.shortcuts import render

from helpdesk.models import Ticket
from admin_automation.models import InternalLetter


def overview(request):

    tickets_count = Ticket.objects.count()

    letters_count = InternalLetter.objects.count()

    context = {
        'tickets_count': tickets_count,
        'letters_count': letters_count,
    }

    return render(
        request,
        'dashboard/overview.html',
        context
    )
