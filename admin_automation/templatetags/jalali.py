from django import template
from django.utils import timezone
import jdatetime

register = template.Library()


@register.filter
def jalali_date(value):
    if not value:
        return ''

    try:
        if timezone.is_aware(value):
            value = timezone.localtime(value)

        jalali = jdatetime.datetime.fromgregorian(datetime=value)

        return jalali.strftime('%Y/%m/%d - %H:%M')

    except Exception:
        return value