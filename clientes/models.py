from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from config.choices import EstadoGeneral, TipoDocumento

solo_letras_validator = RegexValidator(
    regex=r'^[A-Za-zÀ-ÖØ-öø-ÿ ]+$',
    message='Solo se permiten letras y espacios.',
)
telefono_validator = RegexValidator(
    regex=r'^\d{9}$',
    message='El teléfono debe tener exactamente 9 dígitos numéricos.',
)


class ClienteQuerySet(models.QuerySet):
    def activos(self):
        return self.filter(estado=EstadoGeneral.ACTIVO)

    def buscar(self, termino):
        return self.filter(
            models.Q(nombres__icontains=termino)
            | models.Q(apellidos__icontains=termino)
            | models.Q(nro_doc__icontains=termino)
        )


class Cliente(models.Model):
    tipo_doc = models.CharField(max_length=3, choices=TipoDocumento.choices, default=TipoDocumento.DNI)
    nro_doc = models.CharField(max_length=15, unique=True, validators=[RegexValidator(regex=r'^\d+$', message='El número de documento solo debe contener dígitos.')])

    nombres = models.CharField(max_length=100, validators=[solo_letras_validator])
    apellidos = models.CharField(max_length=100, validators=[solo_letras_validator])

    telefono = models.CharField(max_length=15, validators=[telefono_validator], blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)

    estado = models.IntegerField(choices=EstadoGeneral.choices, default=EstadoGeneral.ACTIVO)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    objects = ClienteQuerySet.as_manager()

    def __str__(self):
        return f"{self.apellidos}, {self.nombres}"

    def clean(self):
        if not self.nombres or not self.apellidos or not self.nombres.strip() or not self.apellidos.strip():
            raise ValidationError('Nombres y apellidos son obligatorios.')
        if not self.telefono or len(self.telefono) != 9:
            raise ValidationError('El teléfono debe tener exactamente 9 dígitos.')
        if not self.direccion or not self.direccion.strip():
            raise ValidationError('La dirección no puede estar vacía.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    #  PROPERTIES

    @property
    def nombre_completo(self):
        return f"{self.apellidos}, {self.nombres}"

    @property
    def esta_activo(self):
        return self.estado == EstadoGeneral.ACTIVO

    @property
    def total_encomiendas_enviadas(self):
        return self.envios_remitente.count()

    @property
    def total_envios(self):
        return self.total_encomiendas_enviadas

    class Meta:
        db_table = "clientes"
        ordering = ["apellidos"]