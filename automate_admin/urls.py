from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect


urlpatterns = [

    # صفحه اصلی → ورود
    path(
        '',
        lambda request: redirect('/user/login/')
    ),

    # پنل مدیریت Django
    path(
        'admin/',
        admin.site.urls
    ),

    # ورود و خروج کاربران
    path(
        'user/',
        include('user.urls')
    ),

    # Help Desk
    path(
        'helpdesk/',
        include('helpdesk.urls')
    ),

    # اتوماسیون اداری
    path(
        'admin-automation/',
        include('admin_automation.urls')
    ),

    # درخواست‌ها
    path(
        'workflow/',
        include('workflow.urls')
    ),

    # جلسات
    path(
        'meetings/',
        include('meetings.urls')
    ),

    # اسناد
    path(
        'documents/',
        include('documents.urls')
    ),

    # داشبورد
    path(
        'dashboard/',
        include('dashboard.urls')
    ),

    # مدیریت کاربران
    path(
        'user-management/',
        include('user_management.urls')
    ),

]
