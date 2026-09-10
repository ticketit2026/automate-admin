from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def user_list(request):
    return render(
        request,
        'user_management/user_list.html',
        {}
    )
