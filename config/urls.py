from django.contrib import admin
from django.urls import include, path

admin.site.site_header = 'Sistema de Envíos'
admin.site.site_title = 'Admin Sistema de Envíos'
admin.site.index_title = 'Panel de administración'

urlpatterns = [
    path('', include('envios.urls')),
    path('admin/', admin.site.urls),
]
