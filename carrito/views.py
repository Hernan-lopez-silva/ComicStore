from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import transaction
import json
import random
import string
from decimal import Decimal

from .models import Order, OrderItem, PaymentGateway, PaymentSimulation, Coupon
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

        # Aplicar cupón si fue enviado
        coupon_code = data.get('coupon_code', '').strip().upper()
        coupon_obj = None
        discount = Decimal('0.00')

        if coupon_code:
            try:
                coupon_obj = Coupon.objects.get(code=coupon_code)
                if coupon_obj.is_valid():
                    if coupon_obj.discount_type == 'percentage':
                        discount = subtotal * (coupon_obj.discount_value / 100)
                    else:
                        discount = min(coupon_obj.discount_value, subtotal)
                else:
                    return JsonResponse({'error': 'El cupón no es válido o está expirado'}, status=400)
            except Coupon.DoesNotExist:
                return JsonResponse({'error': 'Cupón no encontrado'}, status=400)

        payment_fee = (subtotal - discount + shipping_cost) * (payment_gateway.processing_fee / 100)
        total = subtotal - discount + shipping_cost + payment_fee

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
                coupon=coupon_obj,
                coupon_code=coupon_code,
                discount=discount,
                subtotal=subtotal,
                shipping_cost=shipping_cost,
                payment_fee=payment_fee,
                total=total,
                notes=shipping_info.get('notes', '')
            )
            if coupon_obj:
                coupon_obj.times_used += 1
                coupon_obj.save(update_fields=['times_used'])
            
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


@require_http_methods(["POST"])
def validate_coupon(request):
    """Validar un cupón y devolver el descuento calculado"""
    try:
        data = json.loads(request.body)
        code = data.get('code', '').strip().upper()
        subtotal = Decimal(str(data.get('subtotal', 0)))

        if not code:
            return JsonResponse({'valid': False, 'message': 'Ingresa un código de cupón'})

        try:
            coupon = Coupon.objects.get(code=code)
        except Coupon.DoesNotExist:
            return JsonResponse({'valid': False, 'message': 'Cupón no encontrado'})

        if not coupon.is_valid():
            return JsonResponse({'valid': False, 'message': 'El cupón no es válido o está expirado'})

        if coupon.discount_type == 'percentage':
            discount = subtotal * (coupon.discount_value / 100)
            label = f'{coupon.discount_value}% de descuento'
        else:
            discount = min(coupon.discount_value, subtotal)
            label = f'Descuento de ${coupon.discount_value:,.0f}'

        return JsonResponse({
            'valid': True,
            'discount': float(discount),
            'label': label,
            'message': f'¡Cupón aplicado! {label}',
        })
    except Exception as e:
        return JsonResponse({'valid': False, 'message': str(e)}, status=500)


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
    """Detalle de orden: dueño, staff, o comprobante por enlace (compra invitado sin user)."""
    order = get_object_or_404(
        Order.objects.select_related('payment_gateway').prefetch_related('items'),
        order_id=order_id,
    )
    if request.user.is_staff:
        pass
    elif order.user_id:
        if not request.user.is_authenticated:
            login_url = reverse('login')
            return redirect(f'{login_url}?next={request.get_full_path()}')
        if order.user_id != request.user.id:
            raise Http404()
    context = {'order': order}
    return render(request, 'order_detail.html', context)


@login_required
def my_orders(request):
    """Historial de compras del usuario con ítems para el listado."""
    orders = (
        Order.objects.filter(user=request.user)
        .select_related('payment_gateway')
        .prefetch_related('items')
        .order_by('-created_at')
    )
    return render(request, 'my_orders.html', {'orders': orders})
