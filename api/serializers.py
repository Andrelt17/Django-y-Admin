"""Serializers for Clientes, Rutas, Encomiendas and HistorialEstado."""

from django.utils import timezone
from rest_framework import serializers

from clientes.models import Cliente
from rutas.models import Ruta
from envios.models import Encomienda, HistorialEstado
from config.choices import EstadoEnvio


class ClienteSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.CharField(read_only=True)
    esta_activo = serializers.BooleanField(read_only=True)

    class Meta:
        model = Cliente
        fields = [
            'id',
            'tipo_doc',
            'nro_doc',
            'nombres',
            'apellidos',
            'telefono',
            'email',
            'direccion',
            'estado',
            'fecha_registro',
            'nombre_completo',
            'esta_activo',
        ]


class RutaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ruta
        fields = ['id', 'codigo', 'origen', 'destino', 'precio_base', 'dias_estimados', 'estado']


class HistorialEstadoSerializer(serializers.ModelSerializer):
    estado_anterior_display = serializers.CharField(read_only=True)
    estado_nuevo_display = serializers.CharField(read_only=True)

    class Meta:
        model = HistorialEstado
        fields = [
            'id',
            'estado_anterior',
            'estado_anterior_display',
            'estado_nuevo',
            'estado_nuevo_display',
            'fecha',
        ]


class EncomiendaSerializer(serializers.ModelSerializer):
    remitente = ClienteSerializer(read_only=True)
    destinatario = ClienteSerializer(read_only=True)
    ruta = RutaSerializer(read_only=True)

    remitente_id = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.all(), source='remitente', write_only=True
    )
    destinatario_id = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.all(), source='destinatario', write_only=True
    )
    ruta_id = serializers.PrimaryKeyRelatedField(
        queryset=Ruta.objects.all(), source='ruta', write_only=True
    )

    peso_kg = serializers.DecimalField(source='peso', max_digits=8, decimal_places=2)
    costo_envio = serializers.DecimalField(
        source='costo', max_digits=10, decimal_places=2, required=False, allow_null=True
    )
    esta_entregada = serializers.BooleanField(read_only=True)
    tiene_retraso = serializers.BooleanField(read_only=True)
    dias_en_transito = serializers.IntegerField(source='dias_transito', read_only=True)
    descripcion_corta = serializers.CharField(read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = Encomienda
        fields = [
            'id',
            'codigo',
            'descripcion',
            'descripcion_corta',
            'peso_kg',
            'costo_envio',
            'remitente',
            'destinatario',
            'ruta',
            'estado',
            'estado_display',
            'fecha_registro',
            'fecha_entrega_est',
            'fecha_entrega_real',
            'esta_entregada',
            'tiene_retraso',
            'dias_en_transito',
            'remitente_id',
            'destinatario_id',
            'ruta_id',
        ]
        read_only_fields = [
            'id',
            'codigo',
            'remitente',
            'destinatario',
            'ruta',
            'estado_display',
            'esta_entregada',
            'tiene_retraso',
            'dias_en_transito',
            'descripcion_corta',
            'fecha_registro',
        ]

    def validate_peso_kg(self, value):
        if value <= 0:
            raise serializers.ValidationError('El peso debe ser mayor a 0.')
        return value

    def validate_costo_envio(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError('El costo de envío no puede ser negativo.')
        return value

    def validate(self, attrs):
        remitente = attrs.get('remitente') or getattr(self.instance, 'remitente', None)
        destinatario = attrs.get('destinatario') or getattr(self.instance, 'destinatario', None)
        ruta = attrs.get('ruta') or getattr(self.instance, 'ruta', None)
        peso = attrs.get('peso') or getattr(self.instance, 'peso', None)
        costo = attrs.get('costo') if 'costo' in attrs else getattr(self.instance, 'costo', None)
        fecha_entrega_est = attrs.get('fecha_entrega_est') or getattr(self.instance, 'fecha_entrega_est', None)

        if remitente and destinatario and remitente == destinatario:
            raise serializers.ValidationError('Remitente y destinatario no pueden ser iguales.')

        if fecha_entrega_est and fecha_entrega_est < timezone.now().date():
            raise serializers.ValidationError({'fecha_entrega_est': 'La fecha de entrega estimada no puede estar en el pasado.'})

        if ruta and peso is not None and costo is not None:
            precio_minimo = ruta.precio_base * peso
            if costo < precio_minimo:
                raise serializers.ValidationError(
                    {'costo_envio': 'El costo de envío no debe ser menor al precio base de la ruta para el peso indicado.'}
                )

        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if request and request.user.is_staff:
            # Staff puede ver todo
            return data
        # Usuarios normales no ven costo interno
        data.pop('costo_envio', None)
        return data


class EncomiendaDetailSerializer(EncomiendaSerializer):
    historial = HistorialEstadoSerializer(source='historialestado_set', many=True, read_only=True)

    class Meta(EncomiendaSerializer.Meta):
        fields = EncomiendaSerializer.Meta.fields + ['historial']


class EncomiendaSerializerV2(serializers.ModelSerializer):
    remitente_nombre = serializers.CharField(source='remitente.nombre_completo', read_only=True)
    destinatario_nombre = serializers.CharField(source='destinatario.nombre_completo', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = Encomienda
        fields = [
            'id',
            'codigo',
            'descripcion',
            'estado',
            'estado_display',
            'remitente_nombre',
            'destinatario_nombre',
            'fecha_registro',
        ]
