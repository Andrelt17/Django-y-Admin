from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from config.choices import EstadoGeneral

solo_letras_validator = RegexValidator(
    regex=r'^[A-Za-zÀ-ÖØ-öø-ÿ ]+$',
    message='Solo se permiten letras y espacios.',
)

class Ruta(models.Model):
    codigo = models.CharField(max_length=10, unique=True)
    origen = models.CharField(max_length=100, validators=[solo_letras_validator])
    destino = models.CharField(max_length=100, validators=[solo_letras_validator])

    precio_base = models.DecimalField(max_digits=10, decimal_places=2)
    dias_estimados = models.PositiveIntegerField()

    estado = models.IntegerField(choices=EstadoGeneral.choices, default=EstadoGeneral.ACTIVO)

    def __str__(self):
        return f"{self.origen} → {self.destino}"

    def clean(self):
        if not self.origen or not self.destino:
            raise ValidationError('Origen y destino son obligatorios.')
        if not self.origen.strip() or not self.destino.strip():
            raise ValidationError('Origen y destino no pueden estar vacíos.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        db_table = "rutas"