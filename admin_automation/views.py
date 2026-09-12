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

    # اگر کاربر اجازه مشاهده همه نامه‌ها را نداشته باشد
    # فقط نامه‌های خودش را می‌بیند
    if not request.user.is_superuser and not request.user.has_perm(
        'admin_automation.view_all_letters'
    ):

        letters = letters.filter(
            Q(created_by=request.user) |
            Q(assigned_to=request.user)
        )

    # جستجو
    search = request.GET.get('search', '').strip()

    if search:

        letters = letters.filter(
            Q(title__icontains=search) |
            Q(content__icontains=search) |
            Q(sent_to__icontains=search)
        )

    # فیلتر نوع نامه
    document_type = request.GET.get(
        'document_type',
        ''
    )

    if document_type:

        letters = letters.filter(
            document_type=document_type
        )

    # فیلتر وضعیت
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


@login_required
def letter_create(request):

    if not request.user.is_superuser and not request.user.has_perm(
        'admin_automation.create_letter'
    ):

        messages.error(
            request,
            'شما دسترسی ایجاد نامه را ندارید.'
        )

        return redirect('letter_list')

    users = User.objects.filter(
        is_active=True
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

        status = request.POST.get(
            'status',
            'draft'
        )

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

    # کنترل دسترسی
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

    return render(
        request,
        'admin_automation/letter_detail.html',
        {
            'letter': letter
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

        letter.status = request.POST.get(
            'status'
        )

        assigned_to_id = request.POST.get(
            'assigned_to'
        )

        if assigned_to_id:

            letter.assigned_to = get_object_or_404(
                User,
                id=assigned_to_id,
                is_active=True
            )

        else:

            letter.assigned_to = None

        if request.FILES.get('file'):

            letter.file = request.FILES.get(
                'file'
            )

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
def letter_send(request, letter_id):

    if not request.user.is_superuser and not request.user.has_perm(
        'admin_automation.send_letter'
    ):

        messages.error(
            request,
            'شما دسترسی ارسال نامه را ندارید.'
        )

        return redirect('letter_list')

    letter = get_object_or_404(
        InternalLetter,
        id=letter_id
    )

    if request.method == 'POST':

        letter.status = 'sent'
        letter.save()

        messages.success(
            request,
            'نامه با موفقیت ارسال شد.'
        )

    return redirect(
        'letter_detail',
        letter_id=letter.id
    )
