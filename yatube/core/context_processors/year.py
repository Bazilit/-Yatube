from django.utils import timezone


def year(request):
    date = timezone.now().year
    return {
        'year': date
    }
