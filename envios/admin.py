from django.contrib import admin
from django.utils.html import format_html
from .models import Encomienda, Empleado, HistorialEstado


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('nombres', 'apellidos', 'email', 'estado')
    search_fields = ('nombres', 'apellidos', 'email')
    list_filter = ('estado',)
    ordering = ('apellidos', 'nombres')


@admin.register(Encomienda)
class EncomiendaAdmin(admin.ModelAdmin):
    list_display = ('descripcion_corta', 'remitente', 'destinatario', 'ruta', 'empleado', 'estado_badge_label', 'fecha_registro', 'tiene_retraso')
    search_fields = ('descripcion', 'remitente__nombres', 'remitente__apellidos', 'destinatario__nombres', 'destinatario__apellidos')
    list_filter = ('estado', 'ruta', 'empleado')
    ordering = ('-fecha_registro',)
    readonly_fields = ('fecha_registro',)
    fieldsets = (
        ('Información básica', {'fields': ('descripcion', 'peso', 'costo', 'estado')}),
        ('Relaciones', {'fields': ('remitente', 'destinatario', 'ruta', 'empleado')}),
        ('Fechas', {'fields': ('fecha_entrega_est', 'fecha_entrega_real', 'fecha_registro')}),
    )

    def estado_badge_label(self, obj):
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            obj.estado_badge,
            obj.get_estado_display()
        )
    estado_badge_label.short_description = 'Estado'


@admin.register(HistorialEstado)
class HistorialEstadoAdmin(admin.ModelAdmin):
    list_display = ('encomienda', 'estado_anterior', 'estado_nuevo', 'fecha')
    search_fields = ('encomienda__descripcion',)
    list_filter = ('estado_anterior', 'estado_nuevo')
    ordering = ('-fecha',)
