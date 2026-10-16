
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Permission
from django.contrib import messages


@login_required
def user_list(request):
    users = User.objects.all().order_by('username')

    return render(
        request,
        'user_management/user_list.html',
        {'users': users}
    )


@login_required
def user_create(request):
    if not request.user.is_superuser:
        messages.error(request, 'شما اجازه ایجاد کاربر را ندارید.')
        return redirect('user_management')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            messages.error(
                request,
                'نام کاربری و رمز عبور الزامی هستند.'
            )
            return redirect('user_create')

        if User.objects.filter(username=username).exists():
            messages.error(
                request,
                'این نام کاربری قبلاً ثبت شده است.'
            )
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
    if not request.user.is_superuser:
        messages.error(
            request,
            'شما اجازه ویرایش کاربران را ندارید.'
        )
        return redirect('user_management')

    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', '').strip()
        user.last_name = request.POST.get('last_name', '').strip()
        user.email = request.POST.get('email', '').strip()
        user.is_active = request.POST.get('is_active') == 'on'

        user.save()

        messages.success(
            request,
            'اطلاعات کاربر با موفقیت ذخیره شد.'
        )
        return redirect('user_management')

    return render(
        request,
        'user_management/user_edit.html',
        {'user_obj': user}
    )


@login_required
def user_password(request, user_id):
    if not request.user.is_superuser:
        messages.error(
            request,
            'شما اجازه تغییر رمز عبور کاربران را ندارید.'
        )
        return redirect('user_management')

    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')

        if not password:
            messages.error(request, 'رمز عبور را وارد کنید.')
            return redirect('user_password', user_id=user.id)

        if password != password_confirm:
            messages.error(
                request,
                'رمزهای عبور یکسان نیستند.'
            )
            return redirect('user_password', user_id=user.id)

        user.set_password(password)
        user.save()

        messages.success(
            request,
            'رمز عبور کاربر با موفقیت تغییر کرد.'
        )
        return redirect('user_management')

    return render(
        request,
        'user_management/user_password.html',
        {'user_obj': user}
    )


@login_required
def user_permissions(request, user_id):
    if not request.user.is_superuser:
        messages.error(
            request,
            'شما اجازه مدیریت دسترسی کاربران را ندارید.'
        )
        return redirect('user_management')

    user = get_object_or_404(User, id=user_id)

    # مجوزهایی که نباید در صفحه مدیریت دسترسی نمایش داده شوند
    # مجوز view_internalletter عمداً مخفی نشده است.
    hidden_codenames = [
        'add_internalletter',
        'change_internalletter',
        'delete_internalletter',
    ]

    permissions = (
        Permission.objects
        .select_related('content_type')
        .exclude(codename__in=hidden_codenames)
        .order_by(
            'content_type__app_label',
            'content_type__model',
            'codename'
        )
    )

    if request.method == 'POST':
        # مجوزهای قابل نمایش در همین صفحه
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
