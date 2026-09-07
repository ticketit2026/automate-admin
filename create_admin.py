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
        username=username,
        defaults={
            "is_staff": True,
            "is_superuser": True,
        }
    )

    if created:
        user.set_password(password)
        user.save()
        print(f"Superuser '{username}' created successfully.")
    else:
        print(f"Superuser '{username}' already exists.")
else:
    print("ADMIN_USERNAME or ADMIN_PASSWORD is not set.")
