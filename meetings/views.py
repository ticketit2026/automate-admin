from django.shortcuts import render
from .models import Meeting

def meeting_list(request):
    meetings = Meeting.objects.all()
    return render(request, 'meetings/meeting_list.html', {'meetings': meetings})