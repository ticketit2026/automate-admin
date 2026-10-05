from django import template
from django.utils import timezone

register = template.Library()


def gregorian_to_jalali(gy, gm, gd):
    """
    تبدیل تاریخ میلادی به تاریخ شمسی (جلالی)
    خروجی: (سال، ماه، روز)
    """

    g_days_in_month = [31, 28, 31, 30, 31, 30,
                       31, 31, 30, 31, 30, 31]

    j_days_in_month = [31, 31, 31, 31, 31, 31,
                       30, 30, 30, 30, 30, 29]

    gy2 = gy - 1600
    gm2 = gm - 1
    gd2 = gd - 1

    g_day_no = (
        365 * gy2
        + (gy2 + 3) // 4
        - (gy2 + 99) // 100
        + (gy2 + 399) // 400
    )

    for i in range(gm2):
        g_day_no += g_days_in_month[i]

    if gm2 > 1 and (
        gy % 4 == 0 and (gy % 100 != 0 or gy % 400 == 0)
    ):
        g_day_no += 1

    g_day_no += gd2

    j_day_no = g_day_no - 79

    j_np = j_day_no // 12053
    j_day_no %= 12053

    jy = 979 + 33 * j_np + 4 * (j_day_no // 1461)

    j_day_no %= 1461

    if j_day_no >= 366:
        jy += (j_day_no - 1) // 365
        j_day_no = (j_day_no - 1) % 365

    i = 0

    while i < 11 and j_day_no >= j_days_in_month[i]:
        j_day_no -= j_days_in_month[i]
        i += 1

    jm = i + 1
    jd = j_day_no + 1

    return jy, jm, jd


@register.filter
def jalali_date(value):
    if not value:
        return ''

    try:
        if timezone.is_aware(value):
            value = timezone.localtime(value)

        jy, jm, jd = gregorian_to_jalali(
            value.year,
            value.month,
            value.day
        )

        return f'{jy:04d}/{jm:02d}/{jd:02d} - {value:%H:%M}'

    except Exception:
        return value
