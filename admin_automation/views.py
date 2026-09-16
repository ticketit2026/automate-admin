from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .models import InternalLetter

@login_required
def letter_list(request):
letters = InternalLetter.objects.select_related(
'created_by',
'assigned_to'
)


if not request.user.is_superuser and not request.user.has_perm(
    'admin_automation.view_all_letters'
):
    letters = letters.filter(
        Q(created_by=request.user) |
        Q(assigned_to=request.user)
    )

search = request.GET.get('search', '').strip()
document_type = request.GET.get('document_type', '').strip()
status = request.GET.get('status', '').strip()

if search:
    letters = letters.filter(
        Q(title__icontains=search) |
        Q(content__icontains=search) |
        Q(sent_to__icontains=search)
    )

if document_type:
    letters = letters.filter(document_type=document_type)

if status:
    letters = letters.filter(status=status)

context = {
    'letters': letters,
    'search': search,
    'document_type': document_type,
    'status': status,
}

return render(
    request,
    'admin_automation/letter_list.html',
    context
)


@login_required
def letter_create(request):
if request.method == 'POST':
title = request.POST.get('title', '').strip()
content = request.POST.get('content', '').strip()
document_type = request.POST.get('document_type', '').strip()
sent_to = request.POST.get('sent_to', '').strip()
assigned_to_id = request.POST.get('assigned_to', '').strip()

    if not title or not content or not document_type or not sent_to:
        messages.error(
            request,
            'لطفاً تمام فیلدهای الزامی را تکمیل کنید.'
        )

        return render(
            request,
            'admin_automation/letter_create.html',
            {
                'users': User.objects.filter(
                    is_active=True
                ).exclude(
                    id=request.user.id
                )
            }
        )

    assigned_to = None

    if assigned_to_id:
        assigned_to = get_object_or_404(
            User,
            id=assigned_to_id,
            is_active=True
        )

    letter = InternalLetter.objects.create(
        title=title,
        content=content,
        document_type=document_type,
        sent_to=sent_to,
        assigned_to=assigned_to,
        created_by=request.user,
        status='pending' if assigned_to else 'draft',
    )

    if 'file' in request.FILES:
        letter.file = request.FILES['file']
        letter.save()

    messages.success(
        request,
        'نامه با موفقیت ایجاد شد.'
    )

    return redirect(
        'letter_detail',
        letter_id=letter.id
    )

users = User.objects.filter(
    is_active=True
).exclude(
    id=request.user.id
)

return render(
    request,
    'admin_automation/letter_create.html',
    {
        'users': users
    }
)


@login_required
def letter_detail(request, letter_id):
letter = get_object_or_404(
InternalLetter.objects.select_related(
'created_by',
'assigned_to'
),
id=letter_id
)


can_view = (
    request.user.is_superuser
    or request.user.has_perm(
        'admin_automation.view_all_letters'
    )
    or letter.created_by == request.user
    or letter.assigned_to == request.user
)

if not can_view:
    messages.error(
        request,
        'شما دسترسی مشاهده این نامه را ندارید.'
    )

    return redirect('letter_list')

can_assign = (
    request.user.is_superuser
    or request.user.has_perm(
        'admin_automation.assign_letter'
    )
    or letter.assigned_to == request.user
)

is_assigned_user = (
    letter.assigned_to == request.user
)

can_approve = (
    request.user.is_superuser
    or is_assigned_user
)

can_reject = (
    request.user.is_superuser
    or is_assigned_user
)

users = User.objects.filter(
    is_active=True
).exclude(
    id=request.user.id
)

context = {
    'letter': letter,
    'users': users,
    'can_assign': can_assign,
    'is_assigned_user': is_assigned_user,
    'can_approve': can_approve,
    'can_reject': can_reject,
}

return render(
    request,
    'admin_automation/letter_detail.html',
    context
)


@login_required
def letter_edit(request, letter_id):
letter = get_object_or_404(
InternalLetter,
id=letter_id
)


if not (
    request.user.is_superuser
    or request.user.has_perm(
        'admin_automation.edit_letter'
    )
    or letter.created_by == request.user
):
    messages.error(
        request,
        'شما دسترسی ویرایش این نامه را ندارید.'
    )

    return redirect(
        'letter_detail',
        letter_id=letter.id
    )

if request.method == 'POST':
    letter.title = request.POST.get(
        'title',
        ''
    ).strip()

    letter.content = request.POST.get(
        'content',
        ''
    ).strip()

    letter.document_type = request.POST.get(
        'document_type',
        ''
    ).strip()

    letter.sent_to = request.POST.get(
        'sent_to',
        ''
    ).strip()

    if 'file' in request.FILES:
        letter.file = request.FILES['file']

    letter.save()

    messages.success(
        request,
        'نامه با موفقیت ویرایش شد.'
    )

    return redirect(
        'letter_detail',
        letter_id=letter.id
    )

users = User.objects.filter(
    is_active=True
).exclude(
    id=request.user.id
)

return render(
    request,
    'admin_automation/letter_create.html',
    {
        'letter': letter,
        'users': users,
        'edit_mode': True,
    }
)


@login_required
def letter_delete(request, letter_id):
letter = get_object_or_404(
InternalLetter,
id=letter_id
)


if not (
    request.user.is_superuser
    or request.user.has_perm(
        'admin_automation.delete_letter'
    )
):
    messages.error(
        request,
        'شما دسترسی حذف این نامه را ندارید.'
    )

    return redirect(
        'letter_detail',
        letter_id=letter.id
    )

if request.method == 'POST':
    letter.delete()

    messages.success(
        request,
        'نامه با موفقیت حذف شد.'
    )

    return redirect('letter_list')

return redirect(
    'letter_detail',
    letter_id=letter.id
)


@login_required
def letter_assign(request, letter_id):
letter = get_object_or_404(
InternalLetter,
id=letter_id
)


can_assign = (
    request.user.is_superuser
    or request.user.has_perm(
        'admin_automation.assign_letter'
    )
    or letter.assigned_to == request.user
)

if not can_assign:
    messages.error(
        request,
        'شما دسترسی ارجاع این نامه را ندارید.'
    )

    return redirect(
        'letter_detail',
        letter_id=letter.id
    )

if request.method != 'POST':
    return redirect(
        'letter_detail',
        letter_id=letter.id
    )

assigned_to_id = request.POST.get(
    'assigned_to',
    ''
).strip()

if not assigned_to_id:
    messages.error(
        request,
        'لطفاً کاربر مقصد را انتخاب کنید.'
    )

    return redirect(
        'letter_detail',
        letter_id=letter.id
    )

assigned_to = get_object_or_404(
    User,
    id=assigned_to_id,
    is_active=True
)

letter.assigned_to = assigned_to
letter.status = 'pending'
letter.save()

messages.success(
    request,
    f'نامه به {assigned_to.get_full_name() or assigned_to.username} ارجاع شد.'
)

return redirect(
    'letter_detail',
    letter_id=letter.id
)


@login_required
def letter_approve(request, letter_id):
letter = get_object_or_404(
InternalLetter,
id=letter_id
)


if request.method != 'POST':
    return redirect(
        'letter_detail',
        letter_id=letter.id
    )

if not (
    request.user.is_superuser
    or letter.assigned_to == request.user
):
    messages.error(
        request,
        'شما مسئول بررسی این نامه نیستید.'
    )

    return redirect(
        'letter_detail',
        letter_id=letter.id
    )

if letter.status != 'pending':
    messages.warning(
        request,
        'این نامه در وضعیت قابل تأیید نیست.'
    )

    return redirect(
        'letter_detail',
        letter_id=letter.id
    )

letter.status = 'approved'
letter.save()

messages.success(
    request,
    'نامه با موفقیت تأیید شد.'
)

return redirect(
    'letter_detail',
    letter_id=letter.id
)

@login_required
def letter_reject(request, letter_id):
letter = get_object_or_404(
InternalLetter,
id=letter_id
)


if request.method != 'POST':
    return redirect(
        'letter_detail',
        letter_id=letter.id
    )

if not (
    request.user.is_superuser
    or letter.assigned_to == request.user
):
    messages.error(
        request,
        'شما مسئول بررسی این نامه نیستید.'
    )

    return redirect(
        'letter_detail',
        letter_id=letter.id
    )

if letter.status != 'pending':
    messages.warning(
        request,
        'این نامه در وضعیت قابل رد نیست.'
    )

    return redirect(
        'letter_detail',
        letter_id=letter.id
    )

letter.status = 'rejected'
letter.save()

messages.success(
    request,
    'نامه با موفقیت رد شد.'
)

return redirect(
    'letter_detail',
    letter_id=letter.id
)
