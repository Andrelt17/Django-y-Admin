from django.db import models

class EstadoGeneral(models.IntegerChoices):
    ACTIVO = 1, 'Activo'
    INACTIVO = 0, 'Inactivo'

class EstadoEnvio(models.TextChoices):
    PENDIENTE = 'PE', 'Pendiente'
    EN_TRANSITO = 'TR', 'En tránsito'
    ENTREGADO = 'EN', 'Entregado'
    CANCELADO = 'CA', 'Cancelado'

class TipoDocumento(models.TextChoices):
    DNI = 'DNI', 'DNI'
    RUC = 'RUC', 'RUC'