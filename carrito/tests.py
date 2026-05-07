from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Coupon, Order, PaymentGateway
from crud.models import Comic

class CarritoViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='normal', password='123')
        self.superuser = User.objects.create_superuser(username='admin', password='123')
        self.cupon = Coupon.objects.create(code="TEST", discount_value=10)
        self.gateway = PaymentGateway.objects.create(name='webpay', display_name='Webpay')
        self.order = Order.objects.create(
            user=self.user,
            email="test@test.com",
            payment_gateway=self.gateway,
            subtotal=1000,
            total=1000,
            payment_status='pending'
        )

    def test_carrito_get(self):
        response = self.client.get(reverse('carrito'))
        self.assertEqual(response.status_code, 200)

    def test_checkout_unauthenticated(self):
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 200)

    def test_checkout_authenticated(self):
        self.client.login(username='normal', password='123')
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 200)

    def test_validate_coupon_invalid(self):
        response = self.client.post(reverse('validate_coupon'), {'codigo': 'WRONG'}, content_type='application/json')
        self.assertEqual(response.json()['valid'], False)

    def test_listar_cupones_superuser(self):
        self.client.login(username='admin', password='123')
        response = self.client.get(reverse('listar_cupones'))
        self.assertEqual(response.status_code, 200)

    def test_listar_cupones_normal(self):
        self.client.login(username='normal', password='123')
        response = self.client.get(reverse('listar_cupones'))
        self.assertEqual(response.status_code, 302)

    def test_crear_cupon_get(self):
        self.client.login(username='admin', password='123')
        response = self.client.get(reverse('crear_cupon'))
        self.assertEqual(response.status_code, 200)
    
    def test_eliminar_cupon(self):
        self.client.login(username='admin', password='123')
        response = self.client.post(reverse('eliminar_cupon', args=[self.cupon.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Coupon.objects.count(), 0)

    def test_my_orders_authenticated(self):
        self.client.login(username='normal', password='123')
        response = self.client.get(reverse('my_orders'))
        self.assertEqual(response.status_code, 200)

    def test_order_detail_owner(self):
        self.client.login(username='normal', password='123')
        response = self.client.get(reverse('order_detail', args=[self.order.order_id]))
        self.assertEqual(response.status_code, 200)

    def test_payment_process(self):
        response = self.client.get(reverse('payment_process', args=[self.order.order_id]))
        self.assertEqual(response.status_code, 200)

    def test_payment_success(self):
        self.order.payment_status = 'completed'
        self.order.save()
        response = self.client.get(reverse('payment_success', args=[self.order.order_id]))
        self.assertEqual(response.status_code, 200)

    def test_create_order(self):
        import json
        comic = Comic.objects.create(title="Batman 2", price=1000)
        data = {
            'cart_items': [{'id': comic.id, 'quantity': 1}],
            'shipping_info': {
                'email': 'test@test.com',
                'name': 'Test User',
                'address': 'Test Address',
                'city': 'Test City',
                'region': 'Test Region'
            },
            'payment_gateway': self.gateway.id
        }
        response = self.client.post(
            reverse('create_order'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(response_data.get('success'))

    def test_simulate_payment(self):
        import json
        data = {'card_number': '1111222233334444'}
        response = self.client.post(
            reverse('simulate_payment', args=[self.order.order_id]),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
