"""API URL routing for the v1 REST interface."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    EncomiendaViewSet,
    ClienteListView,
    RutaListView,
    # FBV
    encomienda_list_create_fbv,
    encomienda_detail_fbv,
    # CBV
    EncomiendaListCreateAPIView,
    EncomiendaRetrieveUpdateDestroyAPIView,
    # Mixins
    EncomiendaListCreateMixin,
    EncomiendaRetrieveUpdateDestroyMixin,
    # Generic
    EncomiendaListCreateGeneric,
    EncomiendaRetrieveUpdateDestroyGeneric,
    # V2
    EncomiendaListAPIViewV2,
)

router = DefaultRouter()
router.register('encomiendas', EncomiendaViewSet, basename='encomienda')

urlpatterns = [
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('clientes/', ClienteListView.as_view(), name='cliente-list'),
    path('rutas/', RutaListView.as_view(), name='ruta-list'),
    # FBV
    path('fbv/encomiendas/', encomienda_list_create_fbv, name='fbv-encomienda-list'),
    path('fbv/encomiendas/<int:pk>/', encomienda_detail_fbv, name='fbv-encomienda-detail'),
    # CBV
    path('apiview/encomiendas/', EncomiendaListCreateAPIView.as_view(), name='apiview-encomienda-list'),
    path('apiview/encomiendas/<int:pk>/', EncomiendaRetrieveUpdateDestroyAPIView.as_view(), name='apiview-encomienda-detail'),
    # Mixins
    path('mixins/encomiendas/', EncomiendaListCreateMixin.as_view(), name='mixin-encomienda-list'),
    path('mixins/encomiendas/<int:pk>/', EncomiendaRetrieveUpdateDestroyMixin.as_view(), name='mixin-encomienda-detail'),
    # Generic
    path('generic/encomiendas/', EncomiendaListCreateGeneric.as_view(), name='generic-encomienda-list'),
    path('generic/encomiendas/<int:pk>/', EncomiendaRetrieveUpdateDestroyGeneric.as_view(), name='generic-encomienda-detail'),
    path('', include(router.urls)),
]

# V2 API
v2_urlpatterns = [
    path('encomiendas/', EncomiendaListAPIViewV2.as_view(), name='v2-encomienda-list'),
]
