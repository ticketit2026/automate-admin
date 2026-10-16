from pathlib import Path
from uuid import uuid4
from io import BytesIO

import pymupdf
from PIL import Image, UnidentifiedImageError

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .models import InternalLetter, LetterAttachment
from .annotation_views import user_can_view_letter


MAX_FILE_SIZE = 30 * 1024 * 1024
MAX_PDF_PAGES = 100

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}


# --------------------------------------------------
# اعتبارسنجی فایل بارگذاری‌شده
# --------------------------------------------------

def validate_uploaded_file(uploaded):
    extension = Path(uploaded.name).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            "فقط فایل PDF یا تصاویر JPG، JPEG، PNG و WEBP مجاز هستند."
        )

    if uploaded.size <= 0:
        raise ValidationError("فایل انتخاب‌شده خالی است.")

    if uploaded.size > MAX_FILE_SIZE:
        raise ValidationError(
            "حداکثر حجم مجاز هر فایل ۳۰ مگابایت است."
        )

    content = uploaded.read()
    uploaded.seek(0)

    if extension == ".pdf":
        if not content.startswith(b"%PDF-"):
            raise ValidationError("فایل انتخاب‌شده PDF معتبر نیست.")

        try:
            with pymupdf.open(
                stream=content,
                filetype="pdf",
            ) as pdf:
                if len(pdf) < 1 or len(pdf) > MAX_PDF_PAGES:
                    raise ValidationError(
                        "تعداد صفحات PDF باید بین ۱ تا ۱۰۰ صفحه باشد."
                    )
        except ValidationError:
            raise
        except Exception:
            raise ValidationError("خواندن فایل PDF ناموفق بود.")

    else:
        try:
            with Image.open(BytesIO(content)) as image:
                if image.format not in {"JPEG", "PNG", "WEBP"}:
                    raise ValidationError(
                        "فرمت واقعی تصویر مجاز نیست."
                    )
                image.verify()

        except ValidationError:
            raise
        except (
            UnidentifiedImageError,
            OSError,
            ValueError,
        ):
            raise ValidationError("فایل تصویر معتبر نیست.")


# --------------------------------------------------
# بررسی دسترسی به نامه و فایل پیوست
# --------------------------------------------------

def get_authorized_attachment(user, attachment_id):
    attachment = get_object_or_404(
        LetterAttachment.objects.select_related("letter"),
        pk=attachment_id,
    )

    if not user_can_view_letter(user, attachment.letter):
        raise Http404("پیوست پیدا نشد.")

    if not attachment.file:
        raise Http404("فایل پیوست موجود نیست.")

    try:
        if not attachment.file.storage.exists(attachment.file.name):
            raise Http404("فایل پیوست موجود نیست.")
    except (OSError, ValueError):
        raise Http404("فایل پیوست قابل دسترسی نیست.")

    return attachment


# --------------------------------------------------
# صفحه مدیریت و بارگذاری پیوست‌ها
# --------------------------------------------------

@login_required
@require_http_methods(["GET", "POST"])
def letter_attachments(request, letter_id):
    letter = get_object_or_404(
        InternalLetter,
        pk=letter_id,
    )

    if not user_can_view_letter(request.user, letter):
        messages.error(
            request,
            "اجازه دسترسی به این نامه را ندارید.",
        )
        return redirect("letter_list")

    if request.method == "POST":
        uploaded = request.FILES.get("attachment")
        description = request.POST.get("description", "").strip()

        if not uploaded:
            messages.error(request, "ابتدا یک فایل انتخاب کن.")
            return redirect(
                "letter_attachments",
                letter_id=letter.pk,
            )

        if len(description) > 250:
            messages.error(
                request,
                "توضیحات فایل نباید بیشتر از ۲۵۰ نویسه باشد.",
            )
            return redirect(
                "letter_attachments",
                letter_id=letter.pk,
            )

        try:
            validate_uploaded_file(uploaded)

            extension = Path(uploaded.name).suffix.lower()
            uploaded.name = f"{uuid4().hex}{extension}"

            LetterAttachment.objects.create(
                letter=letter,
                file=uploaded,
                description=description,
                uploaded_by=request.user,
            )

            messages.success(
                request,
                "پیوست با موفقیت ذخیره شد؛ فایل اصلی نامه تغییر نکرد.",
            )

        except ValidationError as exc:
            for error in exc.messages:
                messages.error(request, error)

        except Exception:
            messages.error(
                request,
                "ذخیره فایل ناموفق بود. فضای ذخیره‌سازی و تنظیمات MEDIA را بررسی کن.",
            )

        return redirect(
            "letter_attachments",
            letter_id=letter.pk,
        )

    attachments = letter.attachments.select_related(
        "uploaded_by"
    ).all()

    return render(
        request,
        "admin_automation/letter_attachments.html",
        {
            "letter": letter,
            "attachments": attachments,
        },
    )


# --------------------------------------------------
# مشاهده یا دانلود پیوست تکمیلی
# --------------------------------------------------

@login_required
def letter_attachment_download(request, attachment_id):
    attachment = get_authorized_attachment(
        request.user,
        attachment_id,
    )

    try:
        file_handle = attachment.file.open("rb")
    except (OSError, ValueError):
        raise Http404("باز کردن فایل پیوست ناموفق بود.")

    filename = Path(attachment.file.name).name
    extension = Path(filename).suffix.lower()

    content_types = {
        ".pdf": "application/pdf",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }

    response = FileResponse(
        file_handle,
        content_type=content_types.get(
            extension,
            "application/octet-stream",
        ),
        as_attachment=request.GET.get("download") == "1",
        filename=filename,
    )

    response["X-Content-Type-Options"] = "nosniff"
    response["Cache-Control"] = "private, no-store"

    return response


# --------------------------------------------------
# مشاهده یا دانلود فایل اصلی نامه
# --------------------------------------------------

@login_required
def letter_original_file_download(request, letter_id):
    letter = get_object_or_404(
        InternalLetter,
        pk=letter_id,
    )

    if not user_can_view_letter(request.user, letter):
        raise Http404("فایل پیدا نشد.")

    if not letter.file:
        raise Http404("این نامه فایل اصلی ندارد.")

    try:
        if not letter.file.storage.exists(letter.file.name):
            raise Http404("فایل اصلی موجود نیست.")

        file_handle = letter.file.open("rb")

    except Http404:
        raise
    except (OSError, ValueError):
        raise Http404("باز کردن فایل اصلی ناموفق بود.")

    filename = Path(letter.file.name).name
    extension = Path(filename).suffix.lower()

    content_types = {
        ".pdf": "application/pdf",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }

    response = FileResponse(
        file_handle,
        content_type=content_types.get(
            extension,
            "application/octet-stream",
        ),
        as_attachment=request.GET.get("download") == "1",
        filename=filename,
    )

    response["X-Content-Type-Options"] = "nosniff"
    response["Cache-Control"] = "private, no-store"

    return response
