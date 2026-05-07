from django.test import TestCase, Client
from django.urls import reverse

class ContactoViewTests(TestCase):
    def test_contacto_get(self):
        client = Client()
        response = client.get(reverse('contacto'))
        self.assertEqual(response.status_code, 200)
