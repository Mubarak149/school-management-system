from .models import SiteSetting

def site_settings(request):
    try:
        settings = SiteSetting.objects.first()
    except SiteSetting.DoesNotExist:
        settings = None
    return {'site_settings': settings}
