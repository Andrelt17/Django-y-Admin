from django.urls import path
from .views import EncomiendaListAPIViewV2

urlpatterns = [
    path('encomiendas/', EncomiendaListAPIViewV2.as_view(), name='v2-encomienda-list'),
]