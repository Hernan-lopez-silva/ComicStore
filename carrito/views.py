from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import transaction
import json
import random
import string
from decimal import Decimal

from .models import Order, OrderItem, PaymentGateway, PaymentSimulation
from crud.models import Comic


def carrito(request):
    """Vista del carrito de compras"""
    context = {}
    return render(request, 'carrito.html', context)


@ensure_csrf_cookie
def checkout(request):
    """Vista de la página de checkout"""
    # Obtener pasarelas de pago activas
    payment_gateways = PaymentGateway.objects.filter(is_active=True)
    
    context = {
        'payment_gateways': payment_gateways,
        'shipping_cost': 5000,
    }
    return render(request, 'checkout.html', context)


@require_http_methods(["POST"])
def create_order(request):
    """Crear una orden de compra desde el carrito"""
    try:
        data = json.loads(request.body)
        
        # Validar datos
        cart_items = data.get('cart_items', [])
        if not cart_items:
            return JsonResponse({'error': 'El carrito está vacío'}, status=400)
        
        # Información de envío
        shipping_info = data.get('shipping_info', {})
        payment_gateway_id = data.get('payment_gateway')
        
        # Validar pasarela de pago
        try:
            payment_gateway = PaymentGateway.objects.get(id=payment_gateway_id, is_active=True)
        except PaymentGateway.DoesNotExist:
            return JsonResponse({'error': 'Pasarela de pago no válida'}, status=400)
        
        # Calcular totales
        subtotal = Decimal('0.00')
        items_to_create = []
        
        for item in cart_items:
            try:
                comic = Comic.objects.get(id=item['id'])
                quantity = int(item['quantity'])
                item_subtotal = Decimal(str(comic.price)) * quantity
                subtotal += item_subtotal
                
                items_to_create.append({
                    'comic': comic,
                    'quantity': quantity,
                    'unit_price': comic.price,
                    'subtotal': item_subtotal
                })
            except Comic.DoesNotExist:
                return JsonResponse({'error': f'Comic con ID {item["id"]} no encontrado'}, status=400)
        
        shipping_cost = Decimal('5000.00')
        payment_fee = (subtotal + shipping_cost) * (payment_gateway.processing_fee / 100)
        total = subtotal + shipping_cost + payment_fee
        
        # Crear la orden con transacción atómica
        with transaction.atomic():
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                email=shipping_info.get('email'),
                phone=shipping_info.get('phone', ''),
                shipping_name=shipping_info.get('name'),
                shipping_address=shipping_info.get('address'),
                shipping_city=shipping_info.get('city'),
                shipping_region=shipping_info.get('region'),
                shipping_postal_code=shipping_info.get('postal_code', ''),
                payment_gateway=payment_gateway,
                subtotal=subtotal,
                shipping_cost=shipping_cost,
                payment_fee=payment_fee,
                total=total,
                notes=shipping_info.get('notes', '')
            )
            
            # Crear items de la orden
            for item_data in items_to_create:
                OrderItem.objects.create(
                    order=order,
                    comic=item_data['comic'],
                    comic_title=item_data['comic'].title,
                    comic_image=item_data['comic'].img_path,
                    unit_price=item_data['unit_price'],
                    quantity=item_data['quantity'],
                    subtotal=item_data['subtotal']
                )
        
        return JsonResponse({
            'success': True,
            'order_id': str(order.order_id),
            'total': float(total),
            'payment_url': f'/carrito/payment/{order.order_id}/'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@ensure_csrf_cookie
def payment_process(request, order_id):
    """Vista para procesar el pago según la pasarela seleccionada"""
    order = get_object_or_404(Order, order_id=order_id)
    
    if order.payment_status == 'completed':
        return redirect('payment_success', order_id=order_id)
    
    context = {
        'order': order,
        'gateway': order.payment_gateway,
    }
    
    # Renderizar template específico según la pasarela
    gateway_name = order.payment_gateway.name
    template_name = f'payment/{gateway_name}.html'
    
    return render(request, template_name, context)


@require_http_methods(["POST"])
def simulate_payment(request, order_id):
    """Simular el procesamiento de un pago"""
    try:
        order = get_object_or_404(Order, order_id=order_id)
        
        if order.payment_status == 'completed':
            return JsonResponse({'error': 'Esta orden ya fue pagada'}, status=400)
        
        data = json.loads(request.body)
        gateway = order.payment_gateway
        
        # Simular respuesta de la pasarela (90% de éxito)
        success = random.random() < 0.9
        
        if success:
            # Generar datos de transacción simulados
            transaction_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
            authorization_code = ''.join(random.choices(string.digits, k=6))
            card_last_digits = ''.join(random.choices(string.digits, k=4))
            
            response_code = '00'
            response_message = 'Transacción aprobada'
            
            # Actualizar orden
            order.payment_status = 'completed'
            order.transaction_id = transaction_id
            order.completed_at = timezone.now()
            order.save()
            
        else:
            response_code = random.choice(['01', '05', '12', '51'])
            response_messages = {
                '01': 'Tarjeta no válida',
                '05': 'Transacción rechazada',
                '12': 'Fondos insuficientes',
                '51': 'Tarjeta expirada'
            }
            response_message = response_messages.get(response_code, 'Error desconocido')
            transaction_id = ''
            authorization_code = ''
            card_last_digits = data.get('card_number', '')[-4:] if data.get('card_number') else ''
            
            order.payment_status = 'failed'
            order.save()
        
        # Guardar simulación
        PaymentSimulation.objects.create(
            order=order,
            gateway=gateway,
            simulated_response=json.dumps(data),
            response_code=response_code,
            response_message=response_message,
            authorization_code=authorization_code,
            card_last_digits=card_last_digits
        )
        
        return JsonResponse({
            'success': success,
            'transaction_id': transaction_id,
            'authorization_code': authorization_code,
            'response_code': response_code,
            'response_message': response_message,
            'order_id': str(order.order_id)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def payment_success(request, order_id):
    """Vista de pago exitoso"""
    order = get_object_or_404(Order, order_id=order_id)
    
    if order.payment_status != 'completed':
        return redirect('payment_failed', order_id=order_id)
    
    # Obtener la última simulación
    last_simulation = order.simulations.last()
    
    context = {
        'order': order,
        'simulation': last_simulation,
    }
    return render(request, 'payment/success.html', context)


def payment_failed(request, order_id):
    """Vista de pago fallido"""
    order = get_object_or_404(Order, order_id=order_id)
    
    # Obtener la última simulación
    last_simulation = order.simulations.last()
    
    context = {
        'order': order,
        'simulation': last_simulation,
    }
    return render(request, 'payment/failed.html', context)


def order_detail(request, order_id):
    """Vista de detalle de una orden"""
    order = get_object_or_404(Order, order_id=order_id)
    
    # Verificar que el usuario tenga permiso para ver esta orden
    if request.user.is_authenticated:
        if order.user and order.user != request.user and not request.user.is_staff:
            return redirect('home')
    
    context = {
        'order': order,
    }
    return render(request, 'order_detail.html', context)


@login_required
def my_orders(request):
    """Vista de órdenes del usuario autenticado"""
    orders = Order.objects.filter(user=request.user).prefetch_related('items')
    
    context = {
        'orders': orders,
    }
    return render(request, 'my_orders.html', context)
