from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied

from .models import Ticket, TicketReply


# ==================================================
# بررسی اینکه کاربر اجازه مشاهده این تیکت را دارد
# ==================================================

def can_view_ticket(user, ticket):

    # اگر اجازه مشاهده همه تیکت‌ها را داشته باشد
    if user.has_perm('helpdesk.view_all_tickets'):
        return True

    # در غیر این صورت فقط تیکت‌های خودش
    return ticket.created_by_id == user.id


# ==================================================
# لیست تیکت‌ها + ایجاد تیکت
# ==================================================

@login_required
def ticket_list(request):

    # ----------------------------------------------
    # ایجاد تیکت جدید
    # ----------------------------------------------

    if request.method == 'POST':

        if not request.user.has_perm(
            'helpdesk.create_ticket'
        ):
            raise PermissionDenied

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

    # ----------------------------------------------
    # نمایش تیکت‌ها
    # ----------------------------------------------

    if request.user.has_perm(
        'helpdesk.view_all_tickets'
    ):

        tickets = Ticket.objects.all().order_by(
            '-created_at'
        )

    else:

        tickets = Ticket.objects.filter(
            created_by=request.user
        ).order_by(
            '-created_at'
        )

    return render(
        request,
        'helpdesk/ticket_list.html',
        {
            'tickets': tickets,

            'can_create_ticket':
                request.user.has_perm(
                    'helpdesk.create_ticket'
                ),

            'can_view_all_tickets':
                request.user.has_perm(
                    'helpdesk.view_all_tickets'
                ),
        }
    )


# ==================================================
# جزئیات تیکت
# ==================================================

@login_required
def ticket_detail(request, ticket_id):

    ticket = get_object_or_404(
        Ticket,
        id=ticket_id
    )

    # بررسی دسترسی مشاهده
    if not can_view_ticket(
        request.user,
        ticket
    ):
        raise PermissionDenied

    replies = ticket.replies.all().order_by(
        'created_at'
    )

    return render(
        request,
        'helpdesk/ticket_detail.html',
        {
            'ticket': ticket,
            'replies': replies,

            'can_edit':
                request.user.has_perm(
                    'helpdesk.edit_ticket'
                ),

            'can_delete':
                request.user.has_perm(
                    'helpdesk.delete_ticket'
                ),

            'can_reply':
                request.user.has_perm(
                    'helpdesk.reply_ticket'
                ),

            'can_change_status':
                request.user.has_perm(
                    'helpdesk.change_ticket_status'
                ),

            'can_assign':
                request.user.has_perm(
                    'helpdesk.assign_ticket'
                ),
        }
    )


# ==================================================
# ویرایش تیکت
# ==================================================

@login_required
def edit_ticket(request, ticket_id):

    # بررسی Permission ویرایش
    if not request.user.has_perm(
        'helpdesk.edit_ticket'
    ):
        raise PermissionDenied

    ticket = get_object_or_404(
        Ticket,
        id=ticket_id
    )

    # بررسی دسترسی به خود تیکت
    if not can_view_ticket(
        request.user,
        ticket
    ):
        raise PermissionDenied

    if request.method == 'POST':

        title = request.POST.get('title')
        description = request.POST.get('description')
        priority = request.POST.get('priority')

        ticket.title = title
        ticket.description = description
        ticket.priority = priority

        ticket.save()

        return redirect(
            'ticket_detail',
            ticket_id=ticket.id
        )

    return render(
        request,
        'helpdesk/edit_ticket.html',
        {
            'ticket': ticket
        }
    )


# ==================================================
# حذف تیکت
# ==================================================

@login_required
def delete_ticket(request, ticket_id):

    # بررسی Permission حذف
    if not request.user.has_perm(
        'helpdesk.delete_ticket'
    ):
        raise PermissionDenied

    ticket = get_object_or_404(
        Ticket,
        id=ticket_id
    )

    # بررسی دسترسی به خود تیکت
    if not can_view_ticket(
        request.user,
        ticket
    ):
        raise PermissionDenied

    if request.method == 'POST':

        ticket.delete()

        return redirect(
            'ticket_list'
        )

    return render(
        request,
        'helpdesk/delete_ticket.html',
        {
            'ticket': ticket
        }
    )


# ==================================================
# ثبت پاسخ به تیکت
# ==================================================

@login_required
def add_ticket_reply(request, ticket_id):

    # بررسی Permission پاسخ
    if not request.user.has_perm(
        'helpdesk.reply_ticket'
    ):
        raise PermissionDenied

    ticket = get_object_or_404(
        Ticket,
        id=ticket_id
    )

    # بررسی دسترسی به تیکت
    if not can_view_ticket(
        request.user,
        ticket
    ):
        raise PermissionDenied

    if request.method == 'POST':

        message = request.POST.get('message')

        if message and message.strip():

            TicketReply.objects.create(
                ticket=ticket,
                user=request.user,
                message=message.strip()
            )

            # اگر بسته بود، با پاسخ دوباره باز شود
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


# ==================================================
# تغییر وضعیت تیکت
# ==================================================

@login_required
def update_ticket_status(request, ticket_id):

    # بررسی Permission
    if not request.user.has_perm(
        'helpdesk.change_ticket_status'
    ):
        raise PermissionDenied

    ticket = get_object_or_404(
        Ticket,
        id=ticket_id
    )

    # بررسی دسترسی به تیکت
    if not can_view_ticket(
        request.user,
        ticket
    ):
        raise PermissionDenied

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


# ==================================================
# ارجاع تیکت به کارشناس
# ==================================================

@login_required
def assign_ticket(request, ticket_id):

    # بررسی Permission
    if not request.user.has_perm(
        'helpdesk.assign_ticket'
    ):
        raise PermissionDenied

    ticket = get_object_or_404(
        Ticket,
        id=ticket_id
    )

    # بررسی دسترسی به تیکت
    if not can_view_ticket(
        request.user,
        ticket
    ):
        raise PermissionDenied

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
