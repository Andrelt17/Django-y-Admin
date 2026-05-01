from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'tipo_doc', 'nro_doc', 'email', 'telefono', 'esta_activo')
    search_fields = ('nombres', 'apellidos', 'nro_doc', 'email')
    list_filter = ('estado', 'tipo_doc')
    ordering = ('apellidos', 'nombres')
    readonly_fields = ('fecha_registro',)
