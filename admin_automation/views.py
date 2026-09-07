from django.shortcuts import render
from .models import InternalLetter

def letter_list(request):
    letters = InternalLetter.objects.all()
    return render(request, 'admin_automation/letter_list.html', {'letters': letters})