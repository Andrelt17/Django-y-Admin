from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

admin.site.site_header = 'Sistema de Envíos'
admin.site.site_title = 'Admin Sistema de Envíos'
admin.site.index_title = 'Panel de administración'

urlpatterns = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/v1/', include('api.urls')),
    path('api/v2/', include('api.urls_v2')),
    path('', include('envios.urls')),
    path('admin/', admin.site.urls),
]
