
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST

from .models import Ticket, TicketReply


VALID_STATUSES = {"open", "in_progress", "closed"}
VALID_PRIORITIES = {"low", "medium", "high"}


# --------------------------------------------------
# بررسی دسترسی
# --------------------------------------------------

def can_view_ticket(user, ticket):
    if not user.is_authenticated:
        return False

    if user.is_superuser or user.has_perm("helpdesk.view_all_tickets"):
        return True

    return (
        ticket.created_by_id == user.id
        or ticket.assigned_to_id == user.id
    )


def get_authorized_ticket(user, ticket_id):
    ticket = get_object_or_404(
        Ticket.objects.select_related("created_by", "assigned_to"),
        pk=ticket_id,
    )

    if not can_view_ticket(user, ticket):
        raise PermissionDenied("اجازه مشاهده این تیکت را ندارید.")

    return ticket


def has_ticket_permission(user, codename):
    return user.is_superuser or user.has_perm(
        f"helpdesk.{codename}"
    )


# --------------------------------------------------
# فهرست، جستجو، فیلتر و ثبت تیکت
# --------------------------------------------------

@login_required
def ticket_list(request):

    if request.method == "POST":
        if not has_ticket_permission(request.user, "create_ticket"):
            messages.error(request, "اجازه ثبت تیکت را ندارید.")
            return redirect("ticket_list")

        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        priority = request.POST.get("priority", "medium").strip()

        if not title or not description:
            messages.error(request, "عنوان و شرح مشکل را وارد کنید.")
            return redirect("ticket_list")

        if len(title) > 200:
            messages.error(request, "عنوان تیکت نباید بیشتر از ۲۰۰ نویسه باشد.")
            return redirect("ticket_list")

        if priority not in VALID_PRIORITIES:
            messages.error(request, "اولویت انتخاب‌شده معتبر نیست.")
            return redirect("ticket_list")

        Ticket.objects.create(
            title=title,
            description=description,
            priority=priority,
            created_by=request.user,
        )

        messages.success(request, "تیکت با موفقیت ثبت شد.")
        return redirect("ticket_list")

    # کاربر دارای مجوز، همه تیکت‌ها را می‌بیند.
    # سایر کاربران فقط تیکت‌های ایجادشده یا ارجاع‌شده به خودشان را می‌بینند.
    if has_ticket_permission(request.user, "view_all_tickets"):
        tickets = Ticket.objects.all()
    else:
        tickets = Ticket.objects.filter(
            Q(created_by=request.user)
            | Q(assigned_to=request.user)
        )

    # جستجو در شماره، عنوان، شرح، ثبت‌کننده و مسئول تیکت
    search_query = request.GET.get("q", "").strip()

    if search_query:
        search_filter = (
            Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(created_by__username__icontains=search_query)
            | Q(created_by__first_name__icontains=search_query)
            | Q(created_by__last_name__icontains=search_query)
            | Q(assigned_to__username__icontains=search_query)
            | Q(assigned_to__first_name__icontains=search_query)
            | Q(assigned_to__last_name__icontains=search_query)
        )

        if search_query.isdigit():
            search_filter |= Q(pk=int(search_query))

        tickets = tickets.filter(search_filter)

    # فیلتر وضعیت
    selected_status = request.GET.get("status", "").strip()

    if selected_status in VALID_STATUSES:
        tickets = tickets.filter(status=selected_status)
    else:
        selected_status = ""

    # فیلتر اولویت
    selected_priority = request.GET.get("priority", "").strip()

    if selected_priority in VALID_PRIORITIES:
        tickets = tickets.filter(priority=selected_priority)
    else:
        selected_priority = ""

    tickets = tickets.select_related(
        "created_by",
        "assigned_to",
    ).order_by("-created_at")

    paginator = Paginator(tickets, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "helpdesk/ticket_list.html",
        {
            "tickets": page_obj,
            "page_obj": page_obj,
            "search_query": search_query,
            "selected_status": selected_status,
            "selected_priority": selected_priority,
            "can_create_ticket": has_ticket_permission(
                request.user, "create_ticket"
            ),
            "can_view_all_tickets": has_ticket_permission(
                request.user, "view_all_tickets"
            ),
            "can_change_status": has_ticket_permission(
                request.user, "change_ticket_status"
            ),
            "can_assign": has_ticket_permission(
                request.user, "assign_ticket"
            ),
        },
    )


# --------------------------------------------------
# جزئیات تیکت
# --------------------------------------------------

@login_required
def ticket_detail(request, ticket_id):
    ticket = get_authorized_ticket(request.user, ticket_id)

    replies = ticket.replies.select_related("user").order_by("created_at")

    return render(
        request,
        "helpdesk/ticket_detail.html",
        {
            "ticket": ticket,
            "replies": replies,
            "can_edit": has_ticket_permission(
                request.user, "change_ticket"
            ),
            "can_delete": has_ticket_permission(
                request.user, "delete_ticket"
            ),
            "can_reply": has_ticket_permission(
                request.user, "reply_ticket"
            ),
            "can_change_status": has_ticket_permission(
                request.user, "change_ticket_status"
            ),
            "can_assign": has_ticket_permission(
                request.user, "assign_ticket"
            ),
        },
    )


# --------------------------------------------------
# ویرایش تیکت
# --------------------------------------------------

@login_required
def edit_ticket(request, ticket_id):
    if not has_ticket_permission(request.user, "change_ticket"):
        raise PermissionDenied("اجازه ویرایش تیکت را ندارید.")

    ticket = get_authorized_ticket(request.user, ticket_id)

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        priority = request.POST.get("priority", "").strip()

        if not title or not description:
            messages.error(request, "عنوان و شرح مشکل الزامی است.")
        elif len(title) > 200:
            messages.error(request, "عنوان نباید بیشتر از ۲۰۰ نویسه باشد.")
        elif priority not in VALID_PRIORITIES:
            messages.error(request, "اولویت انتخاب‌شده معتبر نیست.")
        else:
            ticket.title = title
            ticket.description = description
            ticket.priority = priority
            ticket.save()

            messages.success(request, "تیکت با موفقیت ویرایش شد.")
            return redirect("ticket_detail", ticket_id=ticket.id)

    return render(
        request,
        "helpdesk/edit_ticket.html",
        {"ticket": ticket},
    )


# --------------------------------------------------
# حذف تیکت
# --------------------------------------------------

@login_required
def delete_ticket(request, ticket_id):
    if not has_ticket_permission(request.user, "delete_ticket"):
        raise PermissionDenied("اجازه حذف تیکت را ندارید.")

    ticket = get_authorized_ticket(request.user, ticket_id)

    if request.method == "POST":
        ticket.delete()
        messages.success(request, "تیکت حذف شد.")
        return redirect("ticket_list")

    return render(
        request,
        "helpdesk/delete_ticket.html",
        {"ticket": ticket},
    )


# --------------------------------------------------
# ثبت پاسخ
# --------------------------------------------------

@login_required
@require_POST
def add_ticket_reply(request, ticket_id):
    if not has_ticket_permission(request.user, "reply_ticket"):
        raise PermissionDenied("اجازه پاسخ به تیکت را ندارید.")

    ticket = get_authorized_ticket(request.user, ticket_id)
    message = request.POST.get("message", "").strip()

    if not message:
        messages.error(request, "متن پاسخ را وارد کنید.")
        return redirect("ticket_detail", ticket_id=ticket.id)

    TicketReply.objects.create(
        ticket=ticket,
        user=request.user,
        message=message,
    )

    if ticket.status == "closed":
        ticket.status = "open"
        ticket.save(update_fields=["status", "updated_at"])

    messages.success(request, "پاسخ با موفقیت ثبت شد.")
    return redirect("ticket_detail", ticket_id=ticket.id)


# --------------------------------------------------
# تغییر وضعیت
# --------------------------------------------------

@login_required
def update_ticket_status(request, ticket_id):
    if not has_ticket_permission(request.user, "change_ticket_status"):
        raise PermissionDenied("اجازه تغییر وضعیت تیکت را ندارید.")

    ticket = get_authorized_ticket(request.user, ticket_id)

    if request.method == "POST":
        status = request.POST.get("status", "").strip()

        if status not in VALID_STATUSES:
            messages.error(request, "وضعیت انتخاب‌شده معتبر نیست.")
        else:
            ticket.status = status
            ticket.save(update_fields=["status", "updated_at"])
            messages.success(request, "وضعیت تیکت تغییر کرد.")

        return redirect("ticket_detail", ticket_id=ticket.id)

    return render(
        request,
        "helpdesk/update_ticket_status.html",
        {"ticket": ticket},
    )


# --------------------------------------------------
# ارجاع تیکت به کارشناس
# --------------------------------------------------

@login_required
def assign_ticket(request, ticket_id):
    if not has_ticket_permission(request.user, "assign_ticket"):
        raise PermissionDenied("اجازه ارجاع تیکت را ندارید.")

    ticket = get_authorized_ticket(request.user, ticket_id)
    users = User.objects.filter(is_active=True).order_by(
        "first_name", "last_name", "username"
    )

    if request.method == "POST":
        user_id = request.POST.get("assigned_to", "").strip()

        if not user_id:
            ticket.assigned_to = None
        else:
            try:
                assigned_user = users.get(pk=int(user_id))
                ticket.assigned_to = assigned_user
            except (User.DoesNotExist, ValueError):
                messages.error(request, "کاربر انتخاب‌شده معتبر نیست.")
                return redirect("assign_ticket", ticket_id=ticket.id)

        ticket.save(update_fields=["assigned_to", "updated_at"])
        messages.success(request, "مسئول رسیدگی به تیکت تغییر کرد.")
        return redirect("ticket_detail", ticket_id=ticket.id)

    return render(
        request,
        "helpdesk/assign_ticket.html",
        {
            "ticket": ticket,
            "users": users,
        },
    )
