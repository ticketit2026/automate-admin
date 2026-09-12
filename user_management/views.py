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
        {
            'users': users
        }
    )


@login_required
def user_create(request):

    # فقط ادمین اصلی
    if not request.user.is_superuser:
        return redirect('user_management')

    if request.method == 'POST':

        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')

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
            email=email
        )

        messages.success(
            request,
            'کاربر با موفقیت ایجاد شد.'
        )

        return redirect('user_management')

    return render(
        request,
        'user_management/user_create.html'
    )


@login_required
def user_edit(request, user_id):

    # فقط ادمین اصلی
    if not request.user.is_superuser:
        return redirect('user_management')

    user = get_object_or_404(
        User,
        id=user_id
    )

    if request.method == 'POST':

        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')

        user.is_active = (
            request.POST.get('is_active') == 'on'
        )

        user.save()

        messages.success(
            request,
            'اطلاعات کاربر با موفقیت ذخیره شد.'
        )

        return redirect(
            'user_management'
        )

    return render(
        request,
        'user_management/user_edit.html',
        {
            'user_obj': user
        }
    )


@login_required
def user_password(request, user_id):

    # فقط ادمین اصلی
    if not request.user.is_superuser:
        return redirect('user_management')

    user = get_object_or_404(
        User,
        id=user_id
    )

    if request.method == 'POST':

        password = request.POST.get('password')
        password_confirm = request.POST.get(
            'password_confirm'
        )

        if not password:

            messages.error(
                request,
                'رمز عبور را وارد کنید.'
            )

            return redirect(
                'user_password',
                user_id=user.id
            )

        if password != password_confirm:

            messages.error(
                request,
                'رمزهای عبور یکسان نیستند.'
            )

            return redirect(
                'user_password',
                user_id=user.id
            )

        user.set_password(password)
        user.save()

        messages.success(
            request,
            'رمز عبور کاربر با موفقیت تغییر کرد.'
        )

        return redirect(
            'user_management'
        )

    return render(
        request,
        'user_management/user_password.html',
        {
            'user_obj': user
        }
    )


@login_required
def user_permissions(request, user_id):

    # فقط ادمین اصلی
    if not request.user.is_superuser:
        return redirect('user_management')

    user = get_object_or_404(
        User,
        id=user_id
    )

    permissions = Permission.objects.select_related(
        'content_type'
    ).order_by(
        'content_type__app_label',
        'content_type__model',
        'codename'
    )

    if request.method == 'POST':

        selected_permissions = request.POST.getlist(
            'permissions'
        )

        user.user_permissions.set(
            selected_permissions
        )

        messages.success(
            request,
            'دسترسی‌های کاربر با موفقیت ذخیره شد.'
        )

        return redirect(
            'user_permissions',
            user_id=user.id
        )

    selected_permissions = set(
        user.user_permissions.values_list(
            'id',
            flat=True
        )
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
