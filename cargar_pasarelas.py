import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'comicstore.settings')
django.setup()

from carrito.models import PaymentGateway

def create_payment_gateways():
    gateways = [
        {
            'name': 'webpay',
            'display_name': 'WebPay (Transbank)',
            'is_active': True,
            'logo_url': '',
            'description': 'Paga con tu tarjeta de crédito o débito a través de Transbank',
            'processing_fee': 2.95
        },
        {
            'name': 'paypal',
            'display_name': 'PayPal',
            'is_active': True,
            'logo_url': '',
            'description': 'Paga de forma segura con PayPal',
            'processing_fee': 3.49
        },
        {
            'name': 'mercadopago',
            'display_name': 'Mercado Pago',
            'is_active': True,
            'logo_url': '',
            'description': 'Paga con Mercado Pago - Hasta 12 cuotas sin interés',
            'processing_fee': 4.99
        },
        {
            'name': 'stripe',
            'display_name': 'Stripe',
            'is_active': True,
            'logo_url': '',
            'description': 'Pago seguro procesado por Stripe - Acepta todas las tarjetas',
            'processing_fee': 2.75
        }
    ]
    
    for gateway_data in gateways:
        gateway, created = PaymentGateway.objects.update_or_create(
            name=gateway_data['name'],
            defaults={
                'display_name': gateway_data['display_name'],
                'is_active': gateway_data['is_active'],
                'logo_url': gateway_data['logo_url'],
                'description': gateway_data['description'],
                'processing_fee': gateway_data['processing_fee']
            }
        )
        
        if created:
            print(f'[OK] Pasarela creada: {gateway.display_name}')
        else:
            print(f'[UPDATE] Pasarela actualizada: {gateway.display_name}')
    
    print(f'\nTotal de pasarelas de pago activas: {PaymentGateway.objects.filter(is_active=True).count()}')

if __name__ == '__main__':
    create_payment_gateways()
