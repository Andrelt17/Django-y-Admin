from django.core.exceptions import ValidationError
from django.utils import timezone

def validar_fechas(fecha_est, fecha_real):
    if fecha_est and fecha_est < timezone.now().date():
        raise ValidationError("Fecha estimada no puede ser pasada")

    if fecha_real and fecha_est:
        if fecha_real < fecha_est:
            raise ValidationError("Fecha real no puede ser menor a la estimada")