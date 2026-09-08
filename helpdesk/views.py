from django.shortcuts import render, redirect
from .models import Ticket


def ticket_list(request):

    if request.method == 'POST':

        title = request.POST.get('title')
        description = request.POST.get('description')
        priority = request.POST.get('priority')

        Ticket.objects.create(
            title=title,
            description=description,
            priority=priority,
            created_by=request.user
        )

        return redirect('ticket_list')

    tickets = Ticket.objects.all().order_by('-created_at')

    return render(
        request,
        'helpdesk/ticket_list.html',
        {
            'tickets': tickets
        }
    )
