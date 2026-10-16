from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from django.views.decorators.http import require_GET

@require_GET
def healthz(_request):
    return JsonResponse({'status': 'ok'})

urlpatterns = [
    path('healthz/', healthz, name='healthz'),
    path('backend-admin/', admin.site.urls),
    path('api/', include('core.urls')),
]
