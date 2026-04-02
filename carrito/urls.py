from django.urls import path
from . import views

urlpatterns = [
    path('', views.carrito, name='carrito'),
    path('checkout/', views.checkout, name='checkout'),
    path('create-order/', views.create_order, name='create_order'),
    path('validate-coupon/', views.validate_coupon, name='validate_coupon'),
    path('payment/<uuid:order_id>/', views.payment_process, name='payment_process'),
    path('payment/<uuid:order_id>/simulate/', views.simulate_payment, name='simulate_payment'),
    path('payment/<uuid:order_id>/success/', views.payment_success, name='payment_success'),
    path('payment/<uuid:order_id>/failed/', views.payment_failed, name='payment_failed'),
    path('order/<uuid:order_id>/', views.order_detail, name='order_detail'),
    path('my-orders/', views.my_orders, name='my_orders'),
]
