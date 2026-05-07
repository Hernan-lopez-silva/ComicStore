from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class HomeViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.superuser = User.objects.create_superuser(username='admin', password='password')

    def test_home_unauthenticated_redirects_to_login(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('landing:index'), response.url)

    def test_home_authenticated_standard_user(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_home_authenticated_superuser_redirects(self):
        self.client.login(username='admin', password='password')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('landing:index'))
