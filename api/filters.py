"""Filter definitions for the Encomienda API."""

import django_filters
from django_filters import rest_framework as filters

from envios.models import Encomienda


class EncomiendaFilter(filters.FilterSet):
    estado = filters.CharFilter(field_name='estado')
    ruta = filters.CharFilter(field_name='ruta__codigo')
    remitente = filters.CharFilter(field_name='remitente__nro_doc')
    desde = filters.DateFilter(field_name='fecha_registro', lookup_expr='gte')
    hasta = filters.DateFilter(field_name='fecha_registro', lookup_expr='lte')
    con_retraso = filters.BooleanFilter(method='filter_con_retraso')

    class Meta:
        model = Encomienda
        fields = ['estado', 'ruta', 'remitente', 'desde', 'hasta', 'con_retraso']

    def filter_con_retraso(self, queryset, name, value):
        if value in [True, 'true', 'True', '1', 1]:
            return queryset.con_retraso()
        return queryset
