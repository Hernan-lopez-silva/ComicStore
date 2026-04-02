from django.db import models
from django.contrib.auth.models import User
from crud.models import Comic
import uuid

class PaymentGateway(models.Model):
    """Modelo para las pasarelas de pago disponibles"""
    GATEWAY_CHOICES = [
        ('webpay', 'WebPay (Transbank)'),
        ('paypal', 'PayPal'),
        ('mercadopago', 'Mercado Pago'),
        ('stripe', 'Stripe'),
    ]
    
    name = models.CharField(max_length=50, choices=GATEWAY_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    logo_url = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    processing_fee = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    def __str__(self):
        return self.display_name
    
    class Meta:
        verbose_name = "Pasarela de Pago"
        verbose_name_plural = "Pasarelas de Pago"


class Order(models.Model):
    """Modelo para las órdenes de compra"""
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('processing', 'Procesando'),
        ('completed', 'Completada'),
        ('failed', 'Fallida'),
        ('cancelled', 'Cancelada'),
    ]
    
    order_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    
    # Información de contacto (para usuarios no registrados o como backup)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    
    # Información de envío
    shipping_name = models.CharField(max_length=200)
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100)
    shipping_region = models.CharField(max_length=100)
    shipping_postal_code = models.CharField(max_length=20, blank=True)
    
    # Información de pago
    payment_gateway = models.ForeignKey(PaymentGateway, on_delete=models.SET_NULL, null=True)
    payment_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=200, blank=True)
    
    # Cupón
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, null=True, blank=True)
    coupon_code = models.CharField(max_length=50, blank=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Montos
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=5000.00)
    payment_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Fechas
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Notas
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Orden {self.order_id} - {self.email}"
    
    class Meta:
        verbose_name = "Orden de Compra"
        verbose_name_plural = "Órdenes de Compra"
        ordering = ['-created_at']


class OrderItem(models.Model):
    """Modelo para los items de cada orden"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    comic = models.ForeignKey(Comic, on_delete=models.SET_NULL, null=True)
    
    # Guardamos los datos del comic por si se elimina o cambia de precio
    comic_title = models.CharField(max_length=200)
    comic_image = models.CharField(max_length=300)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.quantity}x {self.comic_title}"
    
    class Meta:
        verbose_name = "Item de Orden"
        verbose_name_plural = "Items de Orden"


class Coupon(models.Model):
    """Modelo para cupones de descuento"""
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Porcentaje'),
        ('fixed', 'Monto fijo'),
    ]

    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, default='percentage')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    max_uses = models.PositiveIntegerField(null=True, blank=True, help_text="Dejar vacío para usos ilimitados")
    times_used = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.code

    def is_valid(self):
        if not self.is_active:
            return False
        if self.max_uses is not None and self.times_used >= self.max_uses:
            return False
        return True

    class Meta:
        verbose_name = "Cupón"
        verbose_name_plural = "Cupones"


class PaymentSimulation(models.Model):
    """Modelo para simular respuestas de pasarelas de pago"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='simulations')
    gateway = models.ForeignKey(PaymentGateway, on_delete=models.CASCADE)
    
    # Simulación
    simulated_response = models.TextField()
    response_code = models.CharField(max_length=50)
    response_message = models.TextField()
    
    # Datos de la transacción simulada
    authorization_code = models.CharField(max_length=100, blank=True)
    card_last_digits = models.CharField(max_length=4, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Simulación {self.gateway} - Orden {self.order.order_id}"
    
    class Meta:
        verbose_name = "Simulación de Pago"
        verbose_name_plural = "Simulaciones de Pago"
