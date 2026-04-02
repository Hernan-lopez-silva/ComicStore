from django.contrib import admin
from .models import PaymentGateway, Order, OrderItem, PaymentSimulation, Coupon


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'is_active', 'times_used', 'max_uses')
    list_filter = ('discount_type', 'is_active')
    search_fields = ('code',)
    list_editable = ('is_active',)


@admin.register(PaymentGateway)
class PaymentGatewayAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'name', 'is_active', 'processing_fee')
    list_filter = ('is_active', 'name')
    search_fields = ('display_name', 'name')
    list_editable = ('is_active',)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('comic', 'comic_title', 'comic_image', 'unit_price', 'quantity', 'subtotal')
    can_delete = False


class PaymentSimulationInline(admin.TabularInline):
    model = PaymentSimulation
    extra = 0
    readonly_fields = ('gateway', 'response_code', 'response_message', 'authorization_code', 'card_last_digits', 'created_at')
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'email', 'shipping_name', 'payment_status', 'payment_gateway', 'total', 'created_at')
    list_filter = ('payment_status', 'payment_gateway', 'created_at')
    search_fields = ('order_id', 'email', 'shipping_name', 'transaction_id')
    readonly_fields = ('order_id', 'created_at', 'updated_at', 'completed_at')
    inlines = [OrderItemInline, PaymentSimulationInline]
    
    fieldsets = (
        ('Información de la Orden', {
            'fields': ('order_id', 'user', 'payment_status', 'transaction_id')
        }),
        ('Información de Contacto', {
            'fields': ('email', 'phone')
        }),
        ('Información de Envío', {
            'fields': ('shipping_name', 'shipping_address', 'shipping_city', 'shipping_region', 'shipping_postal_code')
        }),
        ('Información de Pago', {
            'fields': ('payment_gateway', 'subtotal', 'shipping_cost', 'payment_fee', 'total')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at', 'completed_at')
        }),
        ('Notas', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'comic_title', 'quantity', 'unit_price', 'subtotal')
    list_filter = ('order__created_at',)
    search_fields = ('comic_title', 'order__order_id', 'order__email')
    readonly_fields = ('order', 'comic', 'comic_title', 'comic_image', 'unit_price', 'quantity', 'subtotal')


@admin.register(PaymentSimulation)
class PaymentSimulationAdmin(admin.ModelAdmin):
    list_display = ('order', 'gateway', 'response_code', 'response_message', 'created_at')
    list_filter = ('gateway', 'response_code', 'created_at')
    search_fields = ('order__order_id', 'order__email', 'response_message')
    readonly_fields = ('order', 'gateway', 'simulated_response', 'response_code', 'response_message', 
                      'authorization_code', 'card_last_digits', 'created_at')
