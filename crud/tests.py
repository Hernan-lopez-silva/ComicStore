from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Comic

class CrudViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.superuser = User.objects.create_superuser(username='admin', password='password123')
        self.comic = Comic.objects.create(title="Batman 1", price=1500, img_path="batman.jpg")

    def test_crud_redirect(self):
        response = self.client.get(reverse('crud'))
        self.assertRedirects(response, reverse('login'))

    def test_listar_superuser(self):
        self.client.login(username='admin', password='password123')
        response = self.client.get(reverse('listar'))
        self.assertEqual(response.status_code, 200)

    def test_listar_no_superuser(self):
        User.objects.create_user(username='normal', password='123')
        self.client.login(username='normal', password='123')
        response = self.client.get(reverse('listar'))
        self.assertEqual(response.status_code, 302)

    def test_crear_get(self):
        self.client.login(username='admin', password='password123')
        response = self.client.get(reverse('crear'))
        self.assertEqual(response.status_code, 200)

    def test_crear_post(self):
        self.client.login(username='admin', password='password123')
        response = self.client.post(reverse('crear'), {
            'title': 'Spiderman 2', 'price': 2000, 'img_path': 'spider.jpg', 'description': 'desc'
        })
        self.assertRedirects(response, reverse('listar'))
        self.assertEqual(Comic.objects.count(), 2)

    def test_editar_post(self):
        self.client.login(username='admin', password='password123')
        response = self.client.post(reverse('editar', args=[self.comic.id]), {
            'title': 'Batman 2', 'price': 2500, 'img_path': 'batman2.jpg', 'description': 'desc'
        })
        self.assertRedirects(response, reverse('listar'))
        self.comic.refresh_from_db()
        self.assertEqual(self.comic.title, 'Batman 2')

    def test_eliminar(self):
        self.client.login(username='admin', password='password123')
        response = self.client.post(reverse('eliminar', args=[self.comic.id]))
        self.assertRedirects(response, reverse('listar'))
        self.assertEqual(Comic.objects.count(), 0)
