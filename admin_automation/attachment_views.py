
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
                filetype="pdf"
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
# بررسی دسترسی و وجود فایل پیوست
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
        if not attachment.file.storage.exists(
            attachment.file.name
        ):
            raise Http404("فایل پیوست موجود نیست.")
    except (OSError, ValueError):
        raise Http404("فایل پیوست قابل دسترسی نیست.")

    return attachment


# --------------------------------------------------
# صفحه بارگذاری و فهرست پیوست‌ها
# --------------------------------------------------

@login_required
@require_http_methods(["GET", "POST"])
def letter_attachments(request, letter_id):
    letter = get_object_or_404(
        InternalLetter,
        pk=letter_id,
    )

    if not user_can_view_letter(request.user, letter)
