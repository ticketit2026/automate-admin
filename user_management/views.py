from django.http import HttpResponse
from django.contrib.auth.decorators import login_required


@login_required
def user_list(request):
    return HttpResponse("User Management OK")
