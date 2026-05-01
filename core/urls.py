from django.urls import include, path

urlpatterns = [
    path('', include('envios.urls')),
]
