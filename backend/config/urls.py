from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/internal/v1/', include('apps.core.urls')),
    path('api/internal/v1/intervencion/', include('apps.intervencion_bancaria.urls')),
    path('api/internal/v1/subasta/', include('apps.subasta_privada.urls')),  # <-- NUEVO
    path('api/internal/v1/mesa-de-cambio/', include('apps.mesa_de_cambio.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns += [
            path('__debug__/', include(debug_toolbar.urls)),
        ]