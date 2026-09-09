from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import Ticket, TicketReply


# ==============================
# لیست تیکت‌ها + ثبت تیکت جدید
# ==============================

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


# ==============================
# جزئیات تیکت + پاسخ‌ها
# ==============================

@login_required
def ticket_detail(request, ticket_id):

    ticket = get_object_or_404(
        Ticket,
        id=ticket_id
    )

    replies = ticket.replies.all().order_by('created_at')

    return render(
        request,
        'helpdesk/ticket_detail.html',
        {
            'ticket': ticket,
            'replies': replies
        }
    )


# ==============================
# ثبت پاسخ به تیکت
# ==============================

@login_required
def add_ticket_reply(request, ticket_id):

    ticket = get_object_or_404(
        Ticket,
        id=ticket_id
    )

    if request.method == 'POST':

        message = request.POST.get('message')

        if message and message.strip():

            TicketReply.objects.create(
                ticket=ticket,
                user=request.user,
                message=message.strip()
            )

            # اگر تیکت بسته بوده، با پاسخ دوباره باز شود
            if ticket.status == 'closed':
                ticket.status = 'open'
                ticket.save()

        return redirect(
            'ticket_detail',
            ticket_id=ticket.id
        )

    return redirect(
        'ticket_detail',
        ticket_id=ticket.id
    )


# ==============================
# تغییر وضعیت تیکت
# ==============================

@login_required
def update_ticket_status(request, ticket_id):

    ticket = get_object_or_404(
        Ticket,
        id=ticket_id
    )

    if request.method == 'POST':

        status = request.POST.get('status')

        ticket.status = status

        ticket.save()

        return redirect(
            'ticket_detail',
            ticket_id=ticket.id
        )

    return render(
        request,
        'helpdesk/update_ticket_status.html',
        {
            'ticket': ticket
        }
    )


# ==============================
# ارجاع تیکت به کارشناس
# ==============================

@login_required
def assign_ticket(request, ticket_id):

    ticket = get_object_or_404(
        Ticket,
        id=ticket_id
    )

    users = User.objects.all().order_by(
        'username'
    )

    if request.method == 'POST':

        user_id = request.POST.get(
            'assigned_to'
        )

        if user_id:

            ticket.assigned_to_id = user_id

        else:

            ticket.assigned_to = None

        ticket.save()

        return redirect(
            'ticket_detail',
            ticket_id=ticket.id
        )

    return render(
        request,
        'helpdesk/assign_ticket.html',
        {
            'ticket': ticket,
            'users': users
        }
    )
