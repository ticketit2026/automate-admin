
from io import BytesIO
from pathlib import Path
from uuid import uuid4

import pymupdf
from PIL import Image

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseBadRequest,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET

from .models import InternalLetter


ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".webp", ".bmp"}
MAX_FILE_SIZE = 30 * 1024 * 1024
MAX_ANNOTATION_SIZE = 60 * 1024 * 1024
MAX_PAGES = 100


def user_can_view_letter(user, letter):
    if user.is_superuser:
        return True

    if user.has_perm("admin_automation.view_all_letters"):
        return True

    return (
        letter.created_by_id == user.id
        or letter.assigned_to_id == user.id
    )


def get_letter_or_404(user, letter_id):
    letter = get_object_or_404(InternalLetter, pk=letter_id)

    if not user_can_view_letter(user, letter):
        raise Http404

    if not letter.file:
        raise Http404("فایل پیوست نامه وجود ندارد.")

    extension = Path(letter.file.name).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise Http404("فرمت فایل پشتیبانی نمی‌شود.")

    try:
        if letter.file.size > MAX_FILE_SIZE:
            raise Http404("حجم فایل بیشتر از حد مجاز است.")
    except OSError:
        raise Http404("خواندن فایل امکان‌پذیر نیست.")

    return letter, extension


def read_letter_file(letter):
    with letter.file.open("rb") as source:
        return source.read()


def image_to_pdf(image_bytes):
    """تبدیل تصویر به PDF تک‌صفحه‌ای با پس‌زمینه سفید."""
    with Image.open(BytesIO(image_bytes)) as source:
        image = source.convert("RGBA")

        background = Image.new("RGBA", image.size, "white")
        background.alpha_composite(image)

        output = BytesIO()
        background.convert("RGB").save(output, format="PDF", resolution=150)

        return output.getvalue()


def open_letter_pdf(letter, extension):
    raw = read_letter_file(letter)

    if extension == ".pdf":
        return pymupdf.open(stream=raw, filetype="pdf")

    converted = image_to_pdf(raw)
    return pymupdf.open(stream=converted, filetype="pdf")


def render_page_png(document, page_number):
    page = document[page_number]

    # رندر با MuPDF؛ بدون وابستگی به PDF.js مرورگر.
    scale = min(2.0, 1800 / max(page.rect.width, 1))
    pixmap = page.get_pixmap(
        matrix=pymupdf.Matrix(scale, scale),
        alpha=False,
        annots=True,
    )

    return pixmap.tobytes("png")


@login_required
def letter_annotate(request, letter_id):
    try:
        letter, extension = get_letter_or_404(request.user, letter_id)
    except Http404 as exc:
        messages.error(request, str(exc))
        return redirect(request.META.get("HTTP_REFERER", "/"))

    if request.method == "POST":
        try:
            with open_letter_pdf(letter, extension) as document:
                page_count = len(document)

                if page_count < 1 or page_count > MAX_PAGES:
                    return HttpResponseBadRequest(
                        "تعداد صفحات فایل مجاز نیست."
                    )

                try:
                    submitted_count = int(request.POST.get("page_count", "0"))
                except (TypeError, ValueError):
                    return HttpResponseBadRequest(
                        "تعداد صفحات ارسال‌شده معتبر نیست."
                    )

                if submitted_count != page_count:
                    return HttpResponseBadRequest(
                        "تعداد صفحات با فایل اصلی مطابقت ندارد."
                    )

                overlays = []
                total_size = 0

                for index in range(1, page_count + 1):
                    uploaded = request.FILES.get(f"annotation_{index}")

                    if uploaded is None:
                        return HttpResponseBadRequest(
                            f"لایه حاشیه‌نویسی صفحه {index} ارسال نشده است."
                        )

                    if uploaded.size > MAX_ANNOTATION_SIZE:
                        return HttpResponseBadRequest(
                            "حجم حاشیه‌نویسی بیش از حد مجاز است."
                        )

                    png_bytes = uploaded.read()

                    if not png_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
                        return HttpResponseBadRequest(
                            "فرمت لایه حاشیه‌نویسی باید PNG باشد."
                        )

                    total_size += len(png_bytes)

                    if total_size > MAX_ANNOTATION_SIZE:
                        return HttpResponseBadRequest(
                            "حجم مجموع حاشیه‌نویسی‌ها بیش از حد مجاز است."
                        )

                    overlays.append(png_bytes)

                # لایه‌ها روی صفحات PDF اصلی قرار می‌گیرند.
                # متن اصلی PDF به تصویر تبدیل نمی‌شود.
                for index, png_bytes in enumerate(overlays):
                    page = document[index]
                    page.insert_image(
                        page.rect,
                        stream=png_bytes,
                        overlay=True,
                        keep_proportion=False,
                    )

                output_pdf = document.tobytes(
                    garbage=4,
                    deflate=True,
                )

        except Http404:
            raise
        except Exception:
            return HttpResponseBadRequest(
                "پردازش PDF ناموفق بود. فایل اصلی تغییر نکرد."
            )

        old_name = letter.file.name
        storage = letter.file.storage
        new_name = None

        try:
            filename = f"annotated_{uuid4().hex}.pdf"

            letter.file.save(
                filename,
                ContentFile(output_pdf),
                save=False,
            )

            new_name = letter.file.name
            letter.updated_at = timezone.now()
            letter.save()

        except Exception:
            if new_name and new_name != old_name:
                try:
                    storage.delete(new_name)
                except Exception:
                    pass

            letter.file.name = old_name
            return HttpResponseBadRequest(
                "ذخیره فایل ناموفق بود. فایل قبلی حفظ شد."
            )

        # فایل قبلی فقط بعد از ذخیره موفق فایل جدید حذف می‌شود.
        if old_name and old_name != new_name:
            try:
                storage.delete(old_name)
            except Exception:
                pass

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({
                "ok": True,
                "redirect_url": reverse(
                    "letter_annotate",
                    args=[letter.pk],
                ),
            })

        messages.success(request, "فایل حاشیه‌نویسی‌شده ذخیره شد.")
        return redirect("letter_annotate", letter_id=letter.pk)

    try:
        with open_letter_pdf(letter, extension) as document:
            page_count = len(document)

        if page_count < 1 or page_count > MAX_PAGES:
            messages.error(request, "تعداد صفحات فایل مجاز نیست.")
            return redirect(request.META.get("HTTP_REFERER", "/"))

    except Exception:
        messages.error(request, "فایل PDF قابل پردازش نیست.")
        return redirect(request.META.get("HTTP_REFERER", "/"))

    return render(
        request,
        "admin_automation/letter_annotate.html",
        {
            "letter": letter,
            "page_count": page_count,
            "page_image_url_template": reverse(
                "letter_annotation_page",
                args=[letter.pk, 1],
            ),
        },
    )


@login_required
@require_GET
def letter_annotation_page(request, letter_id, page_number):
    try:
        letter, extension = get_letter_or_404(request.user, letter_id)

        with open_letter_pdf(letter, extension) as document:
            if page_number < 1 or page_number > len(document):
                raise Http404("صفحه موردنظر وجود ندارد.")

            png = render_page_png(document, page_number - 1)

    except Http404:
        raise
    except Exception:
        return HttpResponseBadRequest("نمایش صفحه PDF ناموفق بود.")

    response = HttpResponse(png, content_type="image/png")
    response["Cache-Control"] = "private, no-store"
    response["X-Content-Type-Options"] = "nosniff"
    return response
