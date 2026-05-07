from django.test import TestCase, Client
from django.urls import reverse
from crud.models import Comic

class ProductoViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.comic = Comic.objects.create(title="Batman 1", price=1500)

    def test_producto_success(self):
        response = self.client.get(reverse('producto'), {'id': self.comic.id})
        self.assertEqual(response.status_code, 200)

    def test_producto_not_found(self):
        response = self.client.get(reverse('producto'), {'id': 9999})
        self.assertRedirects(response, '/')
