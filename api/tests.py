from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from clientes.models import Cliente
from envios.models import Empleado, Encomienda
from rutas.models import Ruta


@override_settings(CACHES={
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}, REST_FRAMEWORK={
    'DEFAULT_THROTTLE_CLASSES': [],
    'DEFAULT_THROTTLE_RATES': {},
    'DEFAULT_THROTTLE_CACHE': 'default'
})
class EncomiendaAPITestCase(APITestCase):

    def setUp(self):
        # Crear usuario y empleado
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass')
        self.empleado = Empleado.objects.create(
            nombres='Juan',
            apellidos='Perez',
            email='test@example.com',
            estado=1
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Crear datos de prueba
        self.cliente1 = Cliente.objects.create(
            tipo_doc='DNI',
            nro_doc='12345678',
            nombres='Cliente',
            apellidos='Uno',
            telefono='999999999',
            direccion='Dirección 1'
        )
        self.cliente2 = Cliente.objects.create(
            tipo_doc='DNI',
            nro_doc='87654321',
            nombres='Cliente',
            apellidos='Dos',
            telefono='888888888',
            direccion='Dirección 2'
        )
        self.ruta = Ruta.objects.create(
            codigo='RUT001',
            origen='Lima',
            destino='Arequipa',
            precio_base=50.00,
            dias_estimados=2
        )

    def test_obtener_token(self):
        """Test obtener JWT token"""
        url = reverse('token_obtain_pair')
        data = {'username': 'testuser', 'password': 'testpass'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_list_encomiendas(self):
        """Test listar encomiendas"""
        url = reverse('encomienda-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_encomienda(self):
        """Test detalle de encomienda"""
        encomienda = Encomienda.objects.create(
            descripcion='Paquete de prueba',
            peso=5.0,
            remitente=self.cliente1,
            destinatario=self.cliente2,
            ruta=self.ruta,
            empleado=self.empleado
        )
        url = reverse('encomienda-detail', kwargs={'pk': encomienda.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['descripcion'], 'Paquete de prueba')

    def test_create_encomienda_valida(self):
        """Test crear encomienda válida"""
        url = reverse('encomienda-list')
        data = {
            'descripcion': 'Nuevo paquete',
            'peso_kg': 10.0,
            'remitente_id': self.cliente1.id,
            'destinatario_id': self.cliente2.id,
            'ruta_id': self.ruta.id,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_encomienda_peso_invalido(self):
        """Test error por peso inválido"""
        url = reverse('encomienda-list')
        data = {
            'descripcion': 'Nuevo paquete',
            'peso_kg': -5.0,
            'remitente_id': self.cliente1.id,
            'destinatario_id': self.cliente2.id,
            'ruta_id': self.ruta.id,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_encomienda_remitente_igual_destinatario(self):
        """Test error por remitente igual a destinatario"""
        url = reverse('encomienda-list')
        data = {
            'descripcion': 'Nuevo paquete',
            'peso_kg': 10.0,
            'remitente_id': self.cliente1.id,
            'destinatario_id': self.cliente1.id,
            'ruta_id': self.ruta.id,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cambiar_estado(self):
        """Test cambiar estado de encomienda"""
        encomienda = Encomienda.objects.create(
            descripcion='Paquete de prueba',
            peso=5.0,
            remitente=self.cliente1,
            destinatario=self.cliente2,
            ruta=self.ruta,
            empleado=self.empleado
        )
        url = reverse('encomienda-cambiar-estado', kwargs={'pk': encomienda.pk})
        data = {'estado': 'TR', 'observacion': 'En tránsito'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        encomienda.refresh_from_db()
        self.assertEqual(encomienda.estado, 'TR')