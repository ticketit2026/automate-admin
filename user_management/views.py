
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Permission
from django.contrib import messages


@login_required
def user_list(request):
    """نمایش فهرست کاربران"""
    users = User.objects.all().order_by('username')

    return render(
        request,
        'user_management/user_list.html',
        {'users': users}
    )


@login_required
def user_create(request):
    """ایجاد کاربر جدید"""
    if not request.user.is_superuser:
        messages.error(request, 'اجازه ایجاد کاربر را ندارید.')
        return redirect('user_management')

    if request.method == 'POST':
        username = (request.POST.get('username') or '').strip()
        first_name = (request.POST.get('first_name') or '').strip()
        last_name = (request.POST.get('last_name') or '').strip()
        email = (request.POST.get('email') or '').strip()
        password = request.POST.get('password') or ''

        if not username:
            messages.error(request, 'نام کاربری را وارد کنید.')
            return redirect('user_create')

        if not password:
            messages.error(request, 'رمز عبور را وارد کنید.')
            return redirect('user_create')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'این نام کاربری قبلاً ثبت شده است.')
            return redirect('user_create')

        User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email,
        )

        messages.success(request, 'کاربر با موفقیت ایجاد شد.')
        return redirect('user_management')

    return render(request, 'user_management/user_create.html')


@login_required
def user_edit(request, user_id):
    """ویرایش اطلاعات کاربر"""
    if not request.user.is_superuser:
        messages.error(request, 'اجازه ویرایش کاربران را ندارید.')
        return redirect('user_management')

    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        user.first_name = (request.POST.get('first_name') or '').strip()
        user.last_name = (request.POST.get('last_name') or '').strip()
        user.email = (request.POST.get('email') or '').strip()
        user.is_active = request.POST.get('is_active') == 'on'

        user.save()

        messages.success(request, 'اطلاعات کاربر با موفقیت ذخیره شد.')
        return redirect('user_management')

    return render(
        request,
        'user_management/user_edit.html',
        {'user_obj': user}
    )


@login_required
def user_password(request, user_id):
    """تغییر رمز عبور کاربر"""
    if not request.user.is_superuser:
        messages.error(request, 'اجازه تغییر رمز عبور را ندارید.')
        return redirect('user_management')

    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        password = request.POST.get('password') or ''
        password_confirm = request.POST.get('password_confirm') or ''

        if not password:
            messages.error(request, 'رمز عبور را وارد کنید.')
            return redirect('user_password', user_id=user.id)

        if password != password_confirm:
            messages.error(request, 'رمزهای عبور یکسان نیستند.')
            return redirect('user_password', user_id=user.id)

        user.set_password(password)
        user.save()

        messages.success(request, 'رمز عبور کاربر با موفقیت تغییر کرد.')
        return redirect('user_management')

    return render(
        request,
        'user_management/user_password.html',
        {'user_obj': user}
    )


@login_required
def user_permissions(request, user_id):
    """مدیریت دسترسی‌های مستقیم کاربر با گزینه‌های مجاز و غیرمجاز"""
    if not request.user.is_superuser:
        messages.error(request, 'اجازه مدیریت دسترسی‌ها را ندارید.')
        return redirect('user_management')

    user = get_object_or_404(User, id=user_id)

    # مجوزهای استاندارد نامه اداری مخفی می‌شوند؛
    # مجوزهای اختصاصی فارسی همچنان نمایش داده خواهند شد.
    hidden_codenames = [
        'add_internalletter',
        'change_internalletter',
        'delete_internalletter',
        'view_internalletter',
    ]

    permissions = list(
        Permission.objects
        .select_related('content_type')
        .exclude(
            content_type__app_label='admin_automation',
            content_type__model='internalletter',
            codename__in=hidden_codenames,
        )
        .order_by(
            'content_type__app_label',
            'content_type__model',
            'codename',
        )
    )

    if request.method == 'POST':
        for permission in permissions:
            choice = request.POST.get(
                f'permission_{permission.id}'
            )

            if choice == 'allow':
                user.user_permissions.add(permission)

            elif choice == 'deny':
                user.user_permissions.remove(permission)

        messages.success(
            request,
            'دسترسی‌های کاربر با موفقیت ذخیره شد.'
        )

        return redirect(
            'user_permissions',
            user_id=user.id
        )

    selected_permissions = set(
        user.user_permissions.values_list('id', flat=True)
    )

    return render(
        request,
        'user_management/user_permissions.html',
        {
            'user_obj': user,
            'permissions': permissions,
            'selected_permissions': selected_permissions,
        }
    )
