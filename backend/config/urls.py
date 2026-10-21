from django.contrib import admin
from django.core.cache import cache
from django.db import connections
from django.http import JsonResponse
from django.urls import include, path
from django.views.decorators.http import require_GET

@require_GET
def healthz(_request):
    try:
        connections['default'].ensure_connection()
        cache.get('nexage:healthcheck')
    except Exception:
        return JsonResponse({'status': 'unavailable'}, status=503)
    return JsonResponse({'status': 'ok'})

urlpatterns = [
    path('healthz/', healthz, name='healthz'),
    path('backend-admin/', admin.site.urls),
    path('api/', include('core.urls')),
]
