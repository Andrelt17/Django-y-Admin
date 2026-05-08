"""API views for Encomienda, Cliente, and Ruta resources."""

from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import generics, mixins, serializers, status, views, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from config.choices import EstadoEnvio, EstadoGeneral
from clientes.models import Cliente
from envios.models import Encomienda, Empleado
from rutas.models import Ruta

from .filters import EncomiendaFilter
from .pagination import EncomiendaPagination, ClientePagination, HistorialPagination
from .permissions import EsEmpleadoActivo, EsPropietarioOAdmin
from .serializers import (
    ClienteSerializer,
    EncomiendaDetailSerializer,
    EncomiendaSerializer,
    EncomiendaSerializerV2,
    HistorialEstadoSerializer,
    RutaSerializer,
)


class EncomiendaViewSet(viewsets.ModelViewSet):
    queryset = Encomienda.objects.select_related('remitente', 'destinatario', 'ruta', 'empleado').prefetch_related('historialestado_set')
    serializer_class = EncomiendaSerializer
    permission_classes = [IsAuthenticated, EsEmpleadoActivo]
    pagination_class = EncomiendaPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = EncomiendaFilter
    search_fields = ['codigo', 'remitente__apellidos', 'destinatario__apellidos', 'descripcion']
    ordering_fields = ['fecha_registro', 'peso', 'costo']
    ordering = ['-fecha_registro']

    def get_queryset(self):
        return Encomienda.objects.select_related('remitente', 'destinatario', 'ruta', 'empleado').prefetch_related('historialestado_set')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return EncomiendaDetailSerializer
        return EncomiendaSerializer

    def get_permissions(self):
        permissions = [IsAuthenticated(), EsEmpleadoActivo()]
        if self.action in ['update', 'partial_update', 'destroy', 'cambiar_estado']:
            permissions.append(EsPropietarioOAdmin())
        return permissions

    def perform_create(self, serializer):
        empleado = self._get_request_empleado()
        if not empleado:
            raise serializers.ValidationError({'empleado': 'No existe un empleado activo vinculado al usuario.'})
        serializer.save(empleado=empleado)

    def _get_request_empleado(self):
        user = self.request.user
        if hasattr(user, 'empleado'):
            return getattr(user, 'empleado')
        email = getattr(user, 'email', None)
        if not email:
            return None
        return Empleado.objects.filter(email__iexact=email).first()

    @action(detail=True, methods=['post'])
    @extend_schema(
        summary="Cambiar estado de encomienda",
        description="Cambia el estado de una encomienda y registra el cambio en el historial.",
        request={
            'type': 'object',
            'properties': {
                'estado': {'type': 'string', 'description': 'Nuevo estado (PE, TR, EN, CA)'},
                'observacion': {'type': 'string', 'description': 'Observación opcional'}
            },
            'required': ['estado']
        }
    )
    def cambiar_estado(self, request, pk=None):
        encomienda = self.get_object()
        nuevo_estado = request.data.get('estado')
        if not nuevo_estado:
            return Response({'detail': 'El estado es requerido.'}, status=status.HTTP_400_BAD_REQUEST)

        valores_estado = [choice[0] for choice in EstadoEnvio.choices]
        if nuevo_estado not in valores_estado:
            return Response({'detail': 'Estado inválido.'}, status=status.HTTP_400_BAD_REQUEST)

        if nuevo_estado == encomienda.estado:
            return Response({'detail': 'La encomienda ya tiene ese estado.'}, status=status.HTTP_400_BAD_REQUEST)

        encomienda.cambiar_estado(nuevo_estado)
        serializer = EncomiendaDetailSerializer(encomienda, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    @extend_schema(summary="Encomiendas con retraso", description="Lista encomiendas con retraso.")
    def con_retraso(self, request):
        queryset = self.filter_queryset(self.get_queryset().con_retraso())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    @extend_schema(summary="Encomiendas pendientes", description="Lista encomiendas pendientes.")
    def pendientes(self, request):
        queryset = self.filter_queryset(self.get_queryset().pendientes())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    @extend_schema(summary="Historial de encomienda", description="Obtiene el historial paginado de cambios de estado.")
    def historial(self, request, pk=None):
        encomienda = self.get_object()
        historial = encomienda.historialestado_set.order_by('-fecha')
        paginator = HistorialPagination()
        page = paginator.paginate_queryset(historial, request)
        serializer = HistorialEstadoSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 15, cache='default'))  # Cache 15 minutos
    @extend_schema(summary="Estadísticas de encomiendas", description="Estadísticas generales del sistema.")
    def estadisticas(self, request):
        hoy = timezone.now().date()
        data = {
            'total_activas': Encomienda.objects.activas().count(),
            'en_transito': Encomienda.objects.en_transito().count(),
            'con_retraso': Encomienda.objects.con_retraso().count(),
            'entregadas_hoy': Encomienda.objects.filter(estado=EstadoEnvio.ENTREGADO, fecha_entrega_real=hoy).count(),
        }
        return Response(data)

    @action(detail=False, methods=['post'])
    @extend_schema(
        summary="Crear múltiples encomiendas",
        description="Crea varias encomiendas en una sola request.",
        request={'type': 'array', 'items': EncomiendaSerializer}
    )
    def bulk_create(self, request):
        serializer = EncomiendaSerializer(data=request.data, many=True)
        if serializer.is_valid():
            encomiendas = []
            for item in serializer.validated_data:
                empleado = self._get_request_empleado()
                if not empleado:
                    return Response({'detail': 'No existe un empleado activo vinculado al usuario.'}, status=status.HTTP_400_BAD_REQUEST)
                encomienda = Encomienda.objects.create(empleado=empleado, **item)
                encomiendas.append(encomienda)
            result_serializer = EncomiendaSerializer(encomiendas, many=True)
            return Response(result_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['patch'])
    @extend_schema(
        summary="Cambiar estado múltiple",
        description="Cambia el estado de múltiples encomiendas.",
        request={
            'type': 'object',
            'properties': {
                'ids': {'type': 'array', 'items': {'type': 'integer'}},
                'estado': {'type': 'string'},
                'observacion': {'type': 'string'}
            }
        }
    )
    def bulk_estado(self, request):
        ids = request.data.get('ids', [])
        nuevo_estado = request.data.get('estado')
        observacion = request.data.get('observacion', '')
        if not ids or not nuevo_estado:
            return Response({'detail': 'ids y estado son requeridos.'}, status=status.HTTP_400_BAD_REQUEST)
        encomiendas = Encomienda.objects.filter(id__in=ids)
        errores = []
        for encomienda in encomiendas:
            try:
                encomienda.cambiar_estado(nuevo_estado)
            except Exception as e:
                errores.append(f"Encomienda {encomienda.id}: {str(e)}")
        if errores:
            return Response({'errores': errores}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': f'Estado cambiado para {len(encomiendas)} encomiendas.'})


# FBV - Function Based Views
@api_view(['GET', 'POST'])
def encomienda_list_create_fbv(request):
    if request.method == 'GET':
        encomiendas = Encomienda.objects.select_related('remitente', 'destinatario', 'ruta', 'empleado').all()
        serializer = EncomiendaSerializer(encomiendas, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = EncomiendaSerializer(data=request.data)
        if serializer.is_valid():
            empleado = _get_empleado_from_request(request)
            if not empleado:
                return Response({'detail': 'No existe un empleado activo vinculado al usuario.'}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save(empleado=empleado)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH', 'DELETE'])
def encomienda_detail_fbv(request, pk):
    try:
        encomienda = Encomienda.objects.select_related('remitente', 'destinatario', 'ruta', 'empleado').prefetch_related('historialestado_set').get(pk=pk)
    except Encomienda.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = EncomiendaDetailSerializer(encomienda)
        return Response(serializer.data)
    elif request.method == 'PATCH':
        serializer = EncomiendaSerializer(encomienda, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        encomienda.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# CBV - Class Based Views
class EncomiendaListCreateAPIView(views.APIView):
    def get(self, request):
        encomiendas = Encomienda.objects.select_related('remitente', 'destinatario', 'ruta', 'empleado').all()
        serializer = EncomiendaSerializer(encomiendas, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = EncomiendaSerializer(data=request.data)
        if serializer.is_valid():
            empleado = _get_empleado_from_request(request)
            if not empleado:
                return Response({'detail': 'No existe un empleado activo vinculado al usuario.'}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save(empleado=empleado)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EncomiendaRetrieveUpdateDestroyAPIView(views.APIView):
    def get_object(self, pk):
        try:
            return Encomienda.objects.select_related('remitente', 'destinatario', 'ruta', 'empleado').prefetch_related('historialestado_set').get(pk=pk)
        except Encomienda.DoesNotExist:
            raise serializers.ValidationError('Encomienda no encontrada.')

    def get(self, request, pk):
        encomienda = self.get_object(pk)
        serializer = EncomiendaDetailSerializer(encomienda)
        return Response(serializer.data)

    def patch(self, request, pk):
        encomienda = self.get_object(pk)
        serializer = EncomiendaSerializer(encomienda, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        encomienda = self.get_object(pk)
        encomienda.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Mixins
class EncomiendaListCreateMixin(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = Encomienda.objects.select_related('remitente', 'destinatario', 'ruta', 'empleado')
    serializer_class = EncomiendaSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        empleado = _get_empleado_from_request(self.request)
        if not empleado:
            raise serializers.ValidationError({'empleado': 'No existe un empleado activo vinculado al usuario.'})
        serializer.save(empleado=empleado)


class EncomiendaRetrieveUpdateDestroyMixin(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
    queryset = Encomienda.objects.select_related('remitente', 'destinatario', 'ruta', 'empleado').prefetch_related('historialestado_set')
    serializer_class = EncomiendaSerializer

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return EncomiendaDetailSerializer
        return EncomiendaSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


# Generic Views
class EncomiendaListCreateGeneric(generics.ListCreateAPIView):
    queryset = Encomienda.objects.select_related('remitente', 'destinatario', 'ruta', 'empleado')
    serializer_class = EncomiendaSerializer

    def perform_create(self, serializer):
        empleado = _get_empleado_from_request(self.request)
        if not empleado:
            raise serializers.ValidationError({'empleado': 'No existe un empleado activo vinculado al usuario.'})
        serializer.save(empleado=empleado)


class EncomiendaRetrieveUpdateDestroyGeneric(generics.RetrieveUpdateDestroyAPIView):
    queryset = Encomienda.objects.select_related('remitente', 'destinatario', 'ruta', 'empleado').prefetch_related('historialestado_set')
    serializer_class = EncomiendaSerializer

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return EncomiendaDetailSerializer
        return EncomiendaSerializer


# V2
class EncomiendaListAPIViewV2(generics.ListAPIView):
    queryset = Encomienda.objects.select_related('remitente', 'destinatario', 'ruta', 'empleado')
    serializer_class = EncomiendaSerializerV2


# Helper function
def _get_empleado_from_request(request):
    user = request.user
    if hasattr(user, 'empleado'):
        return getattr(user, 'empleado')
    email = getattr(user, 'email', None)
    if not email:
        return None
    return Empleado.objects.filter(email__iexact=email).first()


class ClienteListView(generics.ListAPIView):
    queryset = Cliente.objects.activos()
    serializer_class = ClienteSerializer
    pagination_class = ClientePagination


class RutaListView(generics.ListAPIView):
    queryset = Ruta.objects.filter(estado=EstadoGeneral.ACTIVO)
    serializer_class = RutaSerializer
    pagination_class = None
