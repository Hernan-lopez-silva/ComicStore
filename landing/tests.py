from django.test import TestCase, Client
from django.urls import reverse
from crud.models import Comic

class LandingViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        Comic.objects.create(title="Spiderman 1", price=1000)

        Comic.objects.create(title="Batman 1", price=1500)

    def test_index_view_status_code(self):
        response = self.client.get(reverse('landing:index'))
        self.assertEqual(response.status_code, 200)

    def test_index_view_search(self):
        response = self.client.get(reverse('landing:index'), {'q': 'Spider'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Spiderman")
        self.assertEqual(len(response.context['comics']), 1)

class ComicstoreViewsTests(TestCase):
    def test_preview_404(self):
        from comicstore.views import preview_404, handler404
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get('/')
        response = preview_404(request)
        self.assertEqual(response.status_code, 200)

        response_404 = handler404(request, Exception())
        self.assertEqual(response_404.status_code, 404)