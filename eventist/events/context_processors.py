from django.utils import timezone

def get_current_time(request):
    return dict(current_time=timezone.now())
