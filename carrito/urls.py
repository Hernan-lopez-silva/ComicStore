from django.urls import path
from . import views

urlpatterns = [
    path('', views.carrito, name='carrito'),
    path('checkout/', views.checkout, name='checkout'),
    path('create-order/', views.create_order, name='create_order'),
    path('validate-coupon/', views.validate_coupon, name='validate_coupon'),
    path('cupones/', views.listar_cupones, name='listar_cupones'),
    path('cupones/crear/', views.crear_cupon, name='crear_cupon'),
    path('cupones/editar/<int:id>/', views.editar_cupon, name='editar_cupon'),
    path('cupones/eliminar/<int:id>/', views.eliminar_cupon, name='eliminar_cupon'),
    path('payment/<uuid:order_id>/', views.payment_process, name='payment_process'),
    path('payment/<uuid:order_id>/simulate/', views.simulate_payment, name='simulate_payment'),
    path('payment/<uuid:order_id>/success/', views.payment_success, name='payment_success'),
    path('payment/<uuid:order_id>/failed/', views.payment_failed, name='payment_failed'),
    path('order/<uuid:order_id>/', views.order_detail, name='order_detail'),
    path('my-orders/', views.my_orders, name='my_orders'),
]
