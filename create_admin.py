import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "automate_admin.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = os.getenv("ADMIN_USERNAME")
password = os.getenv("ADMIN_PASSWORD")

if username and password:
    user, created = User.objects.get_or_create(
        username=username
    )

    user.is_staff = True
    user.is_superuser = True
    user.set_password(password)
    user.save()

    print(f"Admin user '{username}' is ready.")
else:
    print("ADMIN_USERNAME or ADMIN_PASSWORD is not set.")
