from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


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

    if request.method == 'POST':

        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email
        )

        return redirect('user_management')

    return render(
        request,
        'user_management/user_create.html'
    )
