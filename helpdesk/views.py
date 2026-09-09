from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Ticket


@login_required
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


@login_required
def ticket_detail(request, ticket_id):

    ticket = Ticket.objects.get(id=ticket_id)

    return render(
        request,
        'helpdesk/ticket_detail.html',
        {
            'ticket': ticket
        }
    )

@login_required
def update_ticket_status(request, ticket_id):

    ticket = Ticket.objects.get(id=ticket_id)

    if request.method == 'POST':

        status = request.POST.get('status')

        ticket.status = status
        ticket.save()

        return redirect('ticket_detail', ticket_id=ticket.id)

    return render(
        request,
        'helpdesk/update_ticket_status.html',
        {
            'ticket': ticket
        }
    )
