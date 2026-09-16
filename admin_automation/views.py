from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q

from .models import InternalLetter

@login_required
def letter_list(request):

letters = InternalLetter.objects.select_related(
    'created_by',
    'assigned_to'
)

# مدیر سیستم یا کسی که دسترسی مشاهده همه نامه‌ها را دارد
# همه نامه‌ها را می‌بیند.
#
# سایر کاربران فقط نامه‌هایی را می‌بینند که:
# - خودشان ایجاد کرده‌اند
# - یا در حال حاضر به آنها ارجاع شده است.
if not request.user.is_superuser and not request.user.has_perm(
    'admin_automation.view_all_letters'
):

    letters = letters.filter(
        Q(created_by=request.user) |
        Q(assigned_to=request.user)
    )

search = request.GET.get(
    'search',
    ''
).strip()

if search:

    letters = letters.filter(
        Q(title__icontains=search) |
        Q(content__icontains=search) |
        Q(sent_to__icontains=search)
    )

document_type = request.GET.get(
    'document_type',
    ''
)

if document_type:

    letters = letters.filter(
        document_type=document_type
    )

status = request.GET.get(
    'status',
    ''
)

if status:

    letters = letters.filter(
        status=status
    )

return render(
    request,
    'admin_automation/letter_list.html',
    {
        'letters': letters,
        'search': search,
        'selected_document_type': document_type,
        'selected_status': status,
    }
)
```

@login_required
def letter_create(request):

# ایجاد نامه برای همه کاربران مجاز است.
# دیگر بررسی create_letter انجام نمی‌شود.

users = User.objects.filter(
    is_active=True
).exclude(
    id=request.user.id
).order_by('username')

if request.method == 'POST':

    title = request.POST.get(
        'title',
        ''
    ).strip()

    content = request.POST.get(
        'content',
        ''
    ).strip()

    document_type = request.POST.get(
        'document_type'
    )

    sent_to = request.POST.get(
        'sent_to',
        ''
    ).strip()

    assigned_to_id = request.POST.get(
        'assigned_to'
    )

    file = request.FILES.get(
        'file'
    )

    if not title:

        messages.error(
            request,
            'عنوان نامه را وارد کنید.'
        )

        return redirect('letter_create')

    if not content:

        messages.error(
            request,
            'متن نامه را وارد کنید.'
        )

        return redirect('letter_create')

    if not document_type:

        messages.error(
            request,
            'نوع نامه را انتخاب کنید.'
        )

        return redirect('letter_create')

    assigned_to = None

    if assigned_to_id:

        assigned_to = get_object_or_404(
            User,
            id=assigned_to_id,
            is_active=True
        )

        if assigned_to.id == request.user.id:

            messages.error(
                request,
                'نامه را نمی‌توان به خودتان ارجاع داد.'
            )

            return redirect('letter_create')

    # اگر هنگام ایجاد نامه، فردی انتخاب شده باشد
    # وضعیت نامه «در حال بررسی» می‌شود.
    #
    # اگر گیرنده انتخاب نشده باشد،
    # نامه به صورت پیش‌نویس ذخیره می‌شود.
    if assigned_to:

        status = 'pending'

    else:

        status = 'draft'

    letter = InternalLetter.objects.create(
        title=title,
        content=content,
        document_type=document_type,
        sent_to=sent_to,
        status=status,
        assigned_to=assigned_to,
        file=file,
        created_by=request.user
    )

    messages.success(
        request,
        'نامه با موفقیت ثبت شد.'
    )

    return redirect(
        'letter_detail',
        letter_id=letter.id
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

# بررسی دسترسی مشاهده نامه
if not request.user.is_superuser:

    has_access = (
        letter.created_by_id == request.user.id
        or letter.assigned_to_id == request.user.id
        or request.user.has_perm(
            'admin_automation.view_all_letters'
        )
    )

    if not has_access:

        messages.error(
            request,
            'شما اجازه مشاهده این نامه را ندارید.'
        )

        return redirect('letter_list')

# آیا کاربر فعلی همان کسی است که نامه به او ارجاع شده؟
is_assigned_user = (
    letter.assigned_to_id == request.user.id
)

users = User.objects.filter(
    is_active=True
).exclude(
    id=request.user.id
).order_by('username')

# اجازه ارجاع:
# مدیر سیستم
# یا کاربر دارای permission
# یا شخصی که در حال حاضر نامه دست اوست
can_assign = (
    request.user.is_superuser
    or request.user.has_perm(
        'admin_automation.assign_letter'
    )
    or is_assigned_user
)

# فقط شخصی که نامه در اختیار اوست
# می‌تواند آن را تأیید کند.
can_approve = (
    request.user.is_superuser
    or (
        is_assigned_user
        and request.user.has_perm(
            'admin_automation.approve_letter'
        )
    )
)

# فقط شخصی که نامه در اختیار اوست
# می‌تواند آن را رد کند.
can_reject = (
    request.user.is_superuser
    or (
        is_assigned_user
        and request.user.has_perm(
            'admin_automation.reject_letter'
        )
    )
)

return render(
    request,
    'admin_automation/letter_detail.html',
    {
        'letter': letter,
        'users': users,
        'is_assigned_user': is_assigned_user,
        'can_assign': can_assign,
        'can_approve': can_approve,
        'can_reject': can_reject,
    }
)

@login_required
def letter_edit(request, letter_id):


if not request.user.is_superuser and not request.user.has_perm(
    'admin_automation.edit_letter'
):

    messages.error(
        request,
        'شما دسترسی ویرایش نامه را ندارید.'
    )

    return redirect('letter_list')

letter = get_object_or_404(
    InternalLetter,
    id=letter_id
)

users = User.objects.filter(
    is_active=True
).exclude(
    id=request.user.id
).order_by('username')

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
        'document_type'
    )

    letter.sent_to = request.POST.get(
        'sent_to',
        ''
    ).strip()

    assigned_to_id = request.POST.get(
        'assigned_to'
    )

    if assigned_to_id:

        assigned_to = get_object_or_404(
            User,
            id=assigned_to_id,
            is_active=True
        )

        if assigned_to.id == request.user.id:

            messages.error(
                request,
                'نامه را نمی‌توان به خودتان ارجاع داد.'
            )

            return redirect(
                'letter_edit',
                letter_id=letter.id
            )

        letter.assigned_to = assigned_to
        letter.status = 'pending'

    else:

        letter.assigned_to = None
        letter.status = 'draft'

    new_file = request.FILES.get(
        'file'
    )

    if new_file:

        letter.file = new_file

    letter.save()

    messages.success(
        request,
        'نامه با موفقیت ویرایش شد.'
    )

    return redirect(
        'letter_detail',
        letter_id=letter.id
    )

return render(
    request,
    'admin_automation/letter_edit.html',
    {
        'letter': letter,
        'users': users
    }
)


@login_required
def letter_delete(request, letter_id):


if not request.user.is_superuser and not request.user.has_perm(
    'admin_automation.delete_letter'
):

    messages.error(
        request,
        'شما دسترسی حذف نامه را ندارید.'
    )

    return redirect('letter_list')

letter = get_object_or_404(
    InternalLetter,
    id=letter_id
)

if request.method == 'POST':

    letter.delete()

    messages.success(
        request,
        'نامه با موفقیت حذف شد.'
    )

    return redirect('letter_list')

return render(
    request,
    'admin_automation/letter_confirm_delete.html',
    {
        'letter': letter
    }
)


@login_required
def letter_assign(request, letter_id):


letter = get_object_or_404(
    InternalLetter,
    id=letter_id
)

is_allowed = (
    request.user.is_superuser
    or request.user.has_perm(
        'admin_automation.assign_letter'
    )
    or letter.assigned_to_id == request.user.id
)

if not is_allowed:

    messages.error(
        request,
        'شما اجازه ارجاع این نامه را ندارید.'
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
    'assigned_to'
)

if not assigned_to_id:

    messages.error(
        request,
        'شخص مورد نظر برای ارجاع نامه را انتخاب کنید.'
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

if assigned_to.id == request.user.id:

    messages.error(
        request,
        'نامه را نمی‌توان به خودتان ارجاع داد.'
    )

    return redirect(
        'letter_detail',
        letter_id=letter.id
    )

letter.assigned_to = assigned_to

# بعد از هر ارجاع، نامه دوباره در حالت بررسی قرار می‌گیرد.
letter.status = 'pending'

letter.save()

messages.success(
    request,
    f'نامه به '
    f'{assigned_to.get_full_name() or assigned_to.username}'
    f' ارجاع شد.'
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

is_allowed = (
    request.user.is_superuser
    or (
        letter.assigned_to_id == request.user.id
        and request.user.has_perm(
            'admin_automation.approve_letter'
        )
    )
)

if not is_allowed:

    messages.error(
        request,
        'شما اجازه تأیید این نامه را ندارید.'
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

is_allowed = (
    request.user.is_superuser
    or (
        letter.assigned_to_id == request.user.id
        and request.user.has_perm(
            'admin_automation.reject_letter'
        )
    )
)

if not is_allowed:

    messages.error(
        request,
        'شما اجازه رد این نامه را ندارید.'
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
