from django.shortcuts import render
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