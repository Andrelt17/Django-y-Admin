"""Custom permissions for the API based on employee status and ownership."""

from rest_framework import permissions

from config.choices import EstadoGeneral
from envios.models import Empleado


class EsEmpleadoActivo(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_staff or user.is_superuser:
            return True
        empleado = self.get_empleado(user)
        return bool(empleado and empleado.estado == EstadoGeneral.ACTIVO)

    @staticmethod
    def get_empleado(user):
        if hasattr(user, 'empleado'):
            return getattr(user, 'empleado')
        email = getattr(user, 'email', None)
        if not email:
            return None
        return Empleado.objects.filter(email__iexact=email).first()


class EsPropietarioOAdmin(permissions.BasePermission):
    message = 'Permiso denegado. Solo el autor o administrador puede modificar esta encomienda.'

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser:
            return True
        empleado = EsEmpleadoActivo.get_empleado(request.user)
        return bool(empleado and getattr(obj, 'empleado', None) == empleado)
