from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from clientes.models import Cliente
from rutas.models import Ruta
from config.choices import EstadoEnvio, EstadoGeneral
from django.utils import timezone
from .validators import validar_fechas
from .querysets import EncomiendaQuerySet

solo_letras_validator = RegexValidator(
    regex=r'^[A-Za-zÀ-ÖØ-öø-ÿ ]+$',
    message='Solo se permiten letras y espacios.',
)

class Empleado(models.Model):
    nombres = models.CharField(max_length=100, validators=[solo_letras_validator])
    apellidos = models.CharField(max_length=100, validators=[solo_letras_validator])
    email = models.EmailField(unique=True)

    estado = models.IntegerField(choices=EstadoGeneral.choices, default=EstadoGeneral.ACTIVO)

    def __str__(self):
        return f"{self.apellidos}, {self.nombres}"

    def clean(self):
        if not self.nombres.strip() or not self.apellidos.strip():
            raise ValidationError('Nombres y apellidos son obligatorios y sólo pueden contener letras.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Encomienda(models.Model):
    descripcion = models.TextField()
    peso = models.DecimalField(max_digits=8, decimal_places=2)

    remitente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name="envios_remitente")
    destinatario = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name="envios_destinatario")

    ruta = models.ForeignKey(Ruta, on_delete=models.PROTECT)
    empleado = models.ForeignKey(Empleado, on_delete=models.PROTECT)

    estado = models.CharField(max_length=2, choices=EstadoEnvio.choices, default=EstadoEnvio.PENDIENTE)

    costo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_entrega_est = models.DateField(null=True, blank=True)
    fecha_entrega_real = models.DateField(null=True, blank=True)

    objects = EncomiendaQuerySet.as_manager()

    def __str__(self):
        return self.descripcion

    #  VALIDACIONES
    def clean(self):
        if self.remitente == self.destinatario:
            raise ValidationError("Remitente y destinatario no pueden ser iguales")

        validar_fechas(self.fecha_entrega_est, self.fecha_entrega_real)

    def save(self, *args, **kwargs):
        if self.costo is None and self.ruta and self.peso is not None:
            self.costo = self.ruta.precio_base * self.peso
        self.full_clean()
        super().save(*args, **kwargs)

    #  PROPERTIES
    @property
    def esta_entregada(self):
        return self.estado == EstadoEnvio.ENTREGADO

    @property
    def tiene_retraso(self):
        if self.fecha_entrega_est is None:
            return False
        hoy = timezone.now().date()
        return self.fecha_entrega_est < hoy and not self.esta_entregada

    @property
    def dias_transito(self):
        return (timezone.now().date() - self.fecha_registro.date()).days

    @property
    def codigo(self):
        return f"ENV{self.pk:06d}" if self.pk else 'ENV000000'

    @property
    def estado_badge(self):
        return {
            EstadoEnvio.PENDIENTE: 'warning',
            EstadoEnvio.EN_TRANSITO: 'info',
            EstadoEnvio.ENTREGADO: 'success',
            EstadoEnvio.CANCELADO: 'secondary',
        }.get(self.estado, 'dark')

    @property
    def descripcion_corta(self):
        return self.descripcion[:40] + '...' if len(self.descripcion) > 40 else self.descripcion

    def cambiar_estado(self, nuevo_estado):
        if self.estado == nuevo_estado:
            return

        estado_anterior = self.estado
        self.estado = nuevo_estado
        self.save()
        HistorialEstado.objects.create(
            encomienda=self,
            estado_anterior=estado_anterior,
            estado_nuevo=nuevo_estado,
        )

    @classmethod
    def crear_con_costo_calculado(cls, remitente, destinatario, ruta, empleado, descripcion, peso, fecha_entrega_est=None, fecha_entrega_real=None, estado=EstadoEnvio.PENDIENTE):
        costo = ruta.precio_base * Decimal(peso)
        return cls.objects.create(
            descripcion=descripcion,
            peso=peso,
            remitente=remitente,
            destinatario=destinatario,
            ruta=ruta,
            empleado=empleado,
            estado=estado,
            costo=costo,
            fecha_entrega_est=fecha_entrega_est,
            fecha_entrega_real=fecha_entrega_real,
        )


class HistorialEstado(models.Model):
    encomienda = models.ForeignKey(Encomienda, on_delete=models.CASCADE)
    estado_anterior = models.CharField(max_length=2)
    estado_nuevo = models.CharField(max_length=2)
    fecha = models.DateTimeField(auto_now_add=True)

    @property
    def estado_anterior_display(self):
        try:
            return EstadoEnvio(self.estado_anterior).label
        except ValueError:
            return self.estado_anterior

    @property
    def estado_nuevo_display(self):
        try:
            return EstadoEnvio(self.estado_nuevo).label
        except ValueError:
            return self.estado_nuevo

    def __str__(self):
        return f"{self.encomienda} {self.estado_anterior} → {self.estado_nuevo} ({self.fecha:%Y-%m-%d %H:%M})"
