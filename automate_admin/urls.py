from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('', lambda request: redirect('/user/login/')),
    path('admin/', admin.site.urls),
    path('user/', include('user.urls')),
    path('helpdesk/', include('helpdesk.urls')),
    path('admin-automation/', include('admin_automation.urls')),
    path('workflow/', include('workflow.urls')),
    path('meetings/', include('meetings.urls')),
    path('documents/', include('documents.urls')),
    path('dashboard/', include('dashboard.urls')),
]
