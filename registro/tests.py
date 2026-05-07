from django.test import TestCase, Client
from django.urls import reverse
from .models import Pais, Region, Comuna, Cliente
from django.contrib.auth.models import User

class RegistroViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.pais = Pais.objects.create(nombre_pais="Chile")
        self.region = Region.objects.create(nombre_region="Metropolitana", id_pais=self.pais)
        self.comuna = Comuna.objects.create(nombre_comuna="Santiago", id_region=self.region)

    def test_registro_get(self):
        response = self.client.get(reverse('registro'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registro.html')

    def test_todos_los_paises(self):
        response = self.client.get(reverse('todos_los_paises'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]['nombre_pais'], 'Chile')

    def test_regiones_por_pais(self):
        response = self.client.get(reverse('regiones_por_pais', args=[self.pais.id_pais]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_comunas_por_region(self):
        response = self.client.get(reverse('comunas_por_region', args=[self.region.id_region]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_registro_post_invalid(self):
        # Envía POST vacío para que falle la validación
        response = self.client.post(reverse('registro'), {})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context.get('registro_exitoso', False))

    def test_form_cliente_validations(self):
        from .forms import FormCliente
        
        # Prueba Rut malo
        form = FormCliente(data={'rut': '123'})
        form.is_valid()
        self.assertIn('Ingrese rut sin puntos y con guión', form.errors.get('rut', []))
        
        # Prueba telefono malo
        form = FormCliente(data={'telefono': '123'})
        form.is_valid()
        self.assertIn('Ingrese un número con formato +56912345678', form.errors.get('telefono', []))
        
        # Prueba contraseñas no coinciden
        form = FormCliente(data={'password1': 'StrongP@ssw0rd!', 'password2': 'StrongP@ssw0rd!2'})
        form.is_valid()
        error_msg = form.errors.get('password2', [])[0] if form.errors.get('password2') else ""
        self.assertTrue('no coinciden' in error_msg)

    def test_form_cliente_rut_existente(self):
        from .forms import FormCliente
        user = User.objects.create_user(username='test', password='123')
        Cliente.objects.create(user=user, rut='1234567-8', nombre='A', apellido='B', telefono='+56912345678', direccion='D', pais=self.pais, region=self.region, comuna=self.comuna)
        form = FormCliente(data={'rut': '1234567-8'})
        form.is_valid()
        self.assertIn('El rut ya está registrado.', form.errors.get('rut', []))

    def test_form_cliente_save(self):
        from .forms import FormCliente
        data = {
            'username': 'newuser',
            'nombre': 'Test',
            'apellido': 'User',
            'rut': '1111111-1',
            'email': 'test@test.com',
            'telefono': '+56911111111',
            'direccion': 'Calle 123',
            'pais': self.pais.id_pais,
            'region': self.region.id_region,
            'comuna': self.comuna.id_comuna,
            'password1': 'StrongP@ssw0rd!',
            'password2': 'StrongP@ssw0rd!'
        }
        form = FormCliente(data=data)
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(Cliente.objects.count(), 1)
