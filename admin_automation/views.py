
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import InternalLetter


def has_access(user, permission):
    """مدیر اصلی دسترسی کامل دارد؛ سایر کاربران به مجوز نیاز دارند."""
    return user.is_superuser or user.has_perm(
        f'admin_automation.{permission}'
    )


def can_view_letter(user, letter):
    """محدود کردن مشاهده نامه به افراد مجاز."""
    return (
        has_access(user, 'view_all_letters')
        or letter.created_by_id == user.id
        or letter.assigned_to_id == user.id
    )


def get_letter_users(request):
    return User.objects.filter(
        is_active=True
    ).exclude(
        id=request.user.id
    ).order_by('username')


def letter_form_context(request, **extra):
    context = {
        'users': get_letter_users(request),
        'letter_number': '',
        'title': '',
        'content': '',
        'document_type': '',
        'sent_to': '',
        'assigned_to_id': '',
    }
    context.update(extra)
    return context


@login_required
def letter_list(request):
    letters = InternalLetter.objects.select_related(
        'created_by',
        'assigned_to',
        'assigned_by',
        'approved_by',
        'rejected_by',
    )

    if not has_access(request.user, 'view_all_letters'):
        letters = letters.filter(
            Q(created_by=request.user)
            | Q(assigned_to=request.user)
        )

    search = request.GET.get('search', '').strip()
    document_type = request.GET.get('document_type', '').strip()
    status = request.GET.get('status', '').strip()

    if search:
        letters = letters.filter(
            Q(letter_number__icontains=search)
            | Q(title__icontains=search)
            | Q(content__icontains=search)
            | Q(sent_to__icontains=search)
        )

    if document_type:
        letters = letters.filter(document_type=document_type)

    if status:
        letters = letters.filter(status=status)

    return render(
        request,
        'admin_automation/letter_list.html',
        {
            'letters': letters,
            'search': search,
            'document_type': document_type,
            'status': status,
            'document_type_choices': InternalLetter._meta.get_field(
                'document_type'
            ).choices,
            'can_create_letter': has_access(
                request.user, 'create_letter'
            ),
        },
    )


@login_required
def letter_create(request):
    if not has_access(request.user, 'create_letter'):
        messages.error(request, 'شما مجوز ایجاد نامه را ندارید.')
        return redirect('letter_list')

    if request.method != 'POST':
        return render(
            request,
            'admin_automation/letter_create.html',
            letter_form_context(request),
        )

    letter_number = request.POST.get('letter_number', '').strip()
    title = request.POST.get('title', '').strip()
    content = request.POST.get('content', '').strip()
    document_type = request.POST.get('document_type', '').strip()
    sent_to = request.POST.get('sent_to', '').strip()
    assigned_to_id = request.POST.get('assigned_to', '').strip()

    context = letter_form_context(
        request,
        letter_number=letter_number,
        title=title,
        content=content,
        document_type=document_type,
        sent_to=sent_to,
        assigned_to_id=assigned_to_id,
    )

    if not all([
        letter_number, title, content, document_type, sent_to
    ]):
        messages.error(
            request,
            'لطفاً تمام فیلدهای الزامی را تکمیل کنید.'
        )
        return render(
            request,
            'admin_automation/letter_create.html',
            context,
        )

    assigned_to = None

    if assigned_to_id:
        assigned_to = get_object_or_404(
            User,
            id=assigned_to_id,
            is_active=True,
        )

    try:
        letter = InternalLetter.objects.create(
            letter_number=letter_number,
            title=title,
            content=content,
            document_type=document_type,
            sent_to=sent_to,
            assigned_to=assigned_to,
            assigned_by=request.user if assigned_to else None,
            assigned_at=timezone.now() if assigned_to else None,
            created_by=request.user,
            status='pending' if assigned_to else 'draft',
        )

        if request.FILES.get('file'):
            letter.file = request.FILES['file']
            letter.save()

    except IntegrityError:
        messages.error(
            request,
            'این شماره نامه قبلاً ثبت شده است. لطفاً شماره دیگری وارد کنید.'
        )
        return render(
            request,
            'admin_automation/letter_create.html',
            context,
        )

    messages.success(request, 'نامه با موفقیت ایجاد شد.')
    return redirect('letter_detail', letter_id=letter.id)


@login_required
def letter_detail(request, letter_id):
    letter = get_object_or_404(
        InternalLetter.objects.select_related(
            'created_by',
            'assigned_to',
            'assigned_by',
            'approved_by',
            'rejected_by',
        ),
        id=letter_id,
    )

    if not can_view_letter(request.user, letter):
        messages.error(
            request,
            'شما دسترسی مشاهده این نامه را ندارید.'
        )
        return redirect('letter_list')

    is_assigned_user = letter.assigned_to_id == request.user.id

    can_edit = (
        has_access(request.user, 'edit_letter')
        and (
            letter.created_by_id == request.user.id
            or has_access(request.user, 'view_all_letters')
        )
    )

    return render(
        request,
        'admin_automation/letter_detail.html',
        {
            'letter': letter,
            'users': get_letter_users(request),
            'can_edit': can_edit,
            'can_delete': has_access(request.user, 'delete_letter'),
            'can_assign': has_access(request.user, 'assign_letter'),
            'is_assigned_user': is_assigned_user,
            'can_approve': (
                has_access(request.user, 'approve_letter')
                and is_assigned_user
            ),
            'can_reject': (
                has_access(request.user, 'reject_letter')
                and is_assigned_user
            ),
        },
    )


@login_required
def letter_edit(request, letter_id):
    letter = get_object_or_404(InternalLetter, id=letter_id)

    if not can_view_letter(request.user, letter):
        messages.error(request, 'شما دسترسی مشاهده این نامه را ندارید.')
        return redirect('letter_list')

    can_edit = (
        has_access(request.user, 'edit_letter')
        and (
            letter.created_by_id == request.user.id
            or has_access(request.user, 'view_all_letters')
        )
    )

    if not can_edit:
        messages.error(request, 'شما مجوز ویرایش این نامه را ندارید.')
        return redirect('letter_detail', letter_id=letter.id)

    if request.method != 'POST':
        return render(
            request,
            'admin_automation/letter_create.html',
            {
                'letter': letter,
                'users': get_letter_users(request),
                'edit_mode': True,
            },
        )

    letter_number = request.POST.get('letter_number', '').strip()
    title = request.POST.get('title', '').strip()
    content = request.POST.get('content', '').strip()
    document_type = request.POST.get('document_type', '').strip()
    sent_to = request.POST.get('sent_to', '').strip()

    if not all([
        letter_number, title, content, document_type, sent_to
    ]):
        messages.error(
            request,
            'لطفاً تمام فیلدهای الزامی را تکمیل کنید.'
        )
        return render(
            request,
            'admin_automation/letter_create.html',
            {
                'letter': letter,
                'users': get_letter_users(request),
                'edit_mode': True,
            },
        )

    letter.letter_number = letter_number
    letter.title = title
    letter.content = content
    letter.document_type = document_type
    letter.sent_to = sent_to

    if request.FILES.get('file'):
        letter.file = request.FILES['file']

    try:
        letter.save()
    except IntegrityError:
        messages.error(
            request,
            'این شماره نامه قبلاً برای نامه دیگری ثبت شده است.'
        )
        return render(
            request,
            'admin_automation/letter_create.html',
            {
                'letter': letter,
                'users': get_letter_users(request),
                'edit_mode': True,
            },
        )

    messages.success(request, 'نامه با موفقیت ویرایش شد.')
    return redirect('letter_detail', letter_id=letter.id)


@login_required
def letter_delete(request, letter_id):
    letter = get_object_or_404(InternalLetter, id=letter_id)

    if not can_view_letter(request.user, letter):
        messages.error(request, 'شما دسترسی مشاهده این نامه را ندارید.')
        return redirect('letter_list')

    if not has_access(request.user, 'delete_letter'):
        messages.error(request, 'شما مجوز حذف نامه را ندارید.')
        return redirect('letter_detail', letter_id=letter.id)

    if request.method != 'POST':
        return redirect('letter_detail', letter_id=letter.id)

    letter.delete()
    messages.success(request, 'نامه با موفقیت حذف شد.')
    return redirect('letter_list')


@login_required
def letter_assign(request, letter_id):
    letter = get_object_or_404(InternalLetter, id=letter_id)

    if not can_view_letter(request.user, letter):
        messages.error(request, 'شما دسترسی مشاهده این نامه را ندارید.')
        return redirect('letter_list')

    if not has_access(request.user, 'assign_letter'):
        messages.error(request, 'شما مجوز ارجاع نامه را ندارید.')
        return redirect('letter_detail', letter_id=letter.id)

    if request.method != 'POST':
        return redirect('letter_detail', letter_id=letter.id)

    assigned_to_id = request.POST.get('assigned_to', '').strip()

    if not assigned_to_id:
        messages.error(request, 'لطفاً کاربر مقصد را انتخاب کنید.')
        return redirect('letter_detail', letter_id=letter.id)

    assigned_to = get_object_or_404(
        User,
        id=assigned_to_id,
        is_active=True,
    )

    letter.assigned_to = assigned_to
    letter.assigned_by = request.user
    letter.assigned_at = timezone.now()
    letter.status = 'pending'
    letter.approved_by = None
    letter.approved_at = None
    letter.rejected_by = None
    letter.rejected_at = None
    letter.save()

    messages.success(
        request,
        f'نامه به {assigned_to.get_full_name() or assigned_to.username} ارجاع شد.'
    )
    return redirect('letter_detail', letter_id=letter.id)


@login_required
def letter_approve(request, letter_id):
    letter = get_object_or_404(InternalLetter, id=letter_id)

    if not can_view_letter(request.user, letter):
        messages.error(request, 'شما دسترسی مشاهده این نامه را ندارید.')
        return redirect('letter_list')

    if request.method != 'POST':
        return redirect('letter_detail', letter_id=letter.id)

    if not (
        has_access(request.user, 'approve_letter')
        and letter.assigned_to_id == request.user.id
    ):
        messages.error(
            request,
            'برای تأیید نامه باید مجوز تأیید داشته باشید و نامه به شما ارجاع شده باشد.'
        )
        return redirect('letter_detail', letter_id=letter.id)

    if letter.status != 'pending':
        messages.warning(request, 'این نامه در وضعیت قابل تأیید نیست.')
        return redirect('letter_detail', letter_id=letter.id)

    letter.status = 'approved'
    letter.approved_by = request.user
    letter.approved_at = timezone.now()
    letter.rejected_by = None
    letter.rejected_at = None
    letter.save()

    messages.success(request, 'نامه با موفقیت تأیید شد.')
    return redirect('letter_detail', letter_id=letter.id)


@login_required
def letter_reject(request, letter_id):
    letter = get_object_or_404(InternalLetter, id=letter_id)

    if not can_view_letter(request.user, letter):
        messages.error(request, 'شما دسترسی مشاهده این نامه را ندارید.')
        return redirect('letter_list')

    if request.method != 'POST':
        return redirect('letter_detail', letter_id=letter.id)

    if not (
        has_access(request.user, 'reject_letter')
        and letter.assigned_to_id == request.user.id
    ):
        messages.error(
            request,
            'برای رد نامه باید مجوز رد داشته باشید و نامه به شما ارجاع شده باشد.'
        )
        return redirect('letter_detail', letter_id=letter.id)

    if letter.status != 'pending':
        messages.warning(request, 'این نامه در وضعیت قابل رد نیست.')
        return redirect('letter_detail', letter_id=letter.id)

    letter.status = 'rejected'
    letter.rejected_by = request.user
    letter.rejected_at = timezone.now()
    letter.approved_by = None
    letter.approved_at = None
    letter.save()

    messages.success(request, 'نامه با موفقیت رد شد.')
    return redirect('letter_detail', letter_id=letter.id)
