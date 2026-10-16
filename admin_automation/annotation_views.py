
from pathlib import Path
from uuid import uuid4

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import InternalLetter


ALLOWED_EXTENSIONS = {
    ".pdf", ".png", ".jpg", ".jpeg", ".webp", ".bmp"
}

MAX_FILE_SIZE = 30 * 1024 * 1024  # 30 MB


def user_can_view_letter(user, letter):
    return (
        user.is_superuser
        or user.has_perm("admin_automation.view_all_letters")
        or letter.created_by_id == user.id
        or letter.assigned_to_id == user.id
    )


@login_required
def letter_annotate(request, letter_id):
    letter = get_object_or_404(
        InternalLetter.objects.select_related(
            "created_by", "assigned_to"
        ),
        pk=letter_id,
    )

    if not user_can_view_letter(request.user, letter):
        messages.error(
            request,
            "شما اجازه مشاهده این نامه را ندارید."
        )
        return redirect("letter_list")

    if not letter.file:
        messages.error(request, "این نامه فایل پیوست ندارد.")
        return redirect("letter_detail", letter_id=letter.id)

    extension = Path(letter.file.name).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        messages.error(
            request,
            "فرمت فایل پشتیبانی نمی‌شود. فایل باید PDF یا تصویر باشد."
        )
        return redirect("letter_detail", letter_id=letter.id)

    if request.method == "POST":
        uploaded = request.FILES.get("annotated_pdf")

        if not uploaded:
            messages.error(request, "فایل PDF نهایی ارسال نشده است.")
            return redirect("letter_annotate", letter_id=letter.id)

        if uploaded.size > MAX_FILE_SIZE:
            messages.error(
                request,
                "حجم فایل نهایی نباید بیشتر از ۳۰ مگابایت باشد."
            )
            return redirect("letter_annotate", letter_id=letter.id)

        if uploaded.size < 5:
            messages.error(request, "فایل PDF معتبر نیست.")
            return redirect("letter_annotate", letter_id=letter.id)

        uploaded.seek(0)
        if uploaded.read(5) != b"%PDF-":
            messages.error(
                request,
                "فایل ارسالی PDF معتبر نیست."
            )
            return redirect("letter_annotate", letter_id=letter.id)

        uploaded.seek(0)

        old_name = letter.file.name
        storage = letter.file.storage
        new_name = f"annotated_letter_{letter.id}_{uuid4().hex}.pdf"
        stored_name = None

        try:
            letter.file.save(
                new_name,
                ContentFile(uploaded.read()),
                save=False,
            )
            stored_name = letter.file.name

            letter.updated_at = timezone.now()
            letter.save(update_fields=["file", "updated_at"])

        except Exception:
            if stored_name:
                storage.delete(stored_name)

            letter.file.name = old_name
            messages.error(
                request,
                "ذخیره فایل انجام نشد. لطفاً دوباره تلاش کنید."
            )
            return redirect("letter_annotate", letter_id=letter.id)

        # حذف نسخه قبلی فقط پس از ذخیره موفق فایل جدید
        if old_name and old_name != letter.file.name:
            try:
                storage.delete(old_name)
            except Exception:
                # خطای حذف نسخه قدیمی نباید ذخیره موفق را خنثی کند.
                pass

        messages.success(
            request,
            "فایل حاشیه‌نویسی‌شده ذخیره شد و جای پیوست قبلی قرار گرفت."
        )
        return redirect("letter_detail", letter_id=letter.id)

    return render(
        request,
        "admin_automation/letter_annotate.html",
        {
            "letter": letter,
            "file_url": letter.file.url,
            "file_ext": extension,
        },
    )
