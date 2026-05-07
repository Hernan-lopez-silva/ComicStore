from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class LoginViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='normaluser', password='password123')
        self.superuser = User.objects.create_superuser(username='admin', password='password123')
        self.login_url = reverse('login')

    def test_login_get_request(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_login_post_invalid(self):
        response = self.client.post(self.login_url, {'username': 'wrong', 'password': 'wrong'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], None, "El nombre de usuario no está registrado.")

    def test_login_post_valid_normal_user(self):
        response = self.client.post(self.login_url, {'username': 'normaluser', 'password': 'password123'})
        self.assertRedirects(response, reverse('landing:index'))

    def test_login_post_valid_superuser(self):
        response = self.client.post(self.login_url, {'username': 'admin', 'password': 'password123'})
        self.assertRedirects(response, reverse('listar'))
