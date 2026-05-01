from django.db import models
from config.choices import EstadoEnvio
from django.utils import timezone

class EncomiendaQuerySet(models.QuerySet):

    def pendientes(self):
        return self.filter(estado=EstadoEnvio.PENDIENTE)

    def en_transito(self):
        return self.filter(estado=EstadoEnvio.EN_TRANSITO)

    def entregadas(self):
        return self.filter(estado=EstadoEnvio.ENTREGADO)

    def activas(self):
        return self.filter(estado__in=[EstadoEnvio.PENDIENTE, EstadoEnvio.EN_TRANSITO])

    def con_retraso(self):
        hoy = timezone.now().date()
        return self.filter(fecha_entrega_est__lt=hoy).exclude(estado=EstadoEnvio.ENTREGADO)

    def por_ruta(self, ruta):
        return self.filter(ruta=ruta)