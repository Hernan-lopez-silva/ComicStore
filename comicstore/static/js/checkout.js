document.addEventListener('DOMContentLoaded', function() {
    const checkoutForm = document.getElementById('checkoutForm');
    const btnProcessOrder = document.getElementById('btnProcessOrder');
    let processingModal = null;

    // Estado del cupón
    let appliedCoupon = null; // { code, discount }

    // Cargar resumen del carrito
    loadCartSummary();

    // Calcular comisión al cambiar pasarela
    document.querySelectorAll('input[name="payment_gateway"]').forEach(radio => {
        radio.addEventListener('change', updatePaymentFee);
    });

    // Cupón
    document.getElementById('btnApplyCoupon').addEventListener('click', applyCoupon);
    document.getElementById('couponInput').addEventListener('keydown', function(e) {
        if (e.key === 'Enter') { e.preventDefault(); applyCoupon(); }
    });
    
    // Procesar orden
    btnProcessOrder.addEventListener('click', async function() {
        if (!checkoutForm.checkValidity()) {
            checkoutForm.reportValidity();
            return;
        }
        
        const selectedGateway = document.querySelector('input[name="payment_gateway"]:checked');
        if (!selectedGateway) {
            alert('Por favor selecciona un método de pago');
            return;
        }
        
        await createOrder();
    });
    
    function loadCartSummary() {
        const cart = JSON.parse(localStorage.getItem('cart') || '[]');
        const orderSummary = document.getElementById('orderSummary');
        
        if (cart.length === 0) {
            orderSummary.innerHTML = '<p class="text-center text-muted">Tu carrito está vacío</p>';
            btnProcessOrder.disabled = true;
            return;
        }
        
        let html = '';
        let subtotal = 0;
        
        cart.forEach(item => {
            const itemTotal = item.price * item.quantity;
            subtotal += itemTotal;
            
            html += `
                <div class="d-flex justify-content-between mb-2 pb-2 border-bottom">
                    <div>
                        <small>${item.title}</small>
                        <br>
                        <small class="text-muted">Cantidad: ${item.quantity}</small>
                    </div>
                    <div class="text-end">
                        <small>$${itemTotal.toLocaleString('es-CL')}</small>
                    </div>
                </div>
            `;
        });
        
        orderSummary.innerHTML = html;
        
        // Actualizar totales
        const shippingCost = 5000;
        document.getElementById('summarySubtotal').textContent = `$${subtotal.toLocaleString('es-CL')}`;
        document.getElementById('summaryShipping').textContent = `$${shippingCost.toLocaleString('es-CL')}`;
        
        // Calcular comisión inicial
        updatePaymentFee();
    }
    
    function updatePaymentFee() {
        const cart = JSON.parse(localStorage.getItem('cart') || '[]');
        let subtotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        const shippingCost = 5000;
        const discount = appliedCoupon ? appliedCoupon.discount : 0;
        const selectedGateway = document.querySelector('input[name="payment_gateway"]:checked');

        if (!selectedGateway) return;

        // Obtener el porcentaje de comisión del texto
        const gatewayCard = selectedGateway.closest('.form-check');
        const feeText = gatewayCard.querySelector('.badge');
        let feePercentage = 0;

        if (feeText) {
            const match = feeText.textContent.match(/\d+\.?\d*/);
            feePercentage = match ? parseFloat(match[0]) : 0;
        }

        const discountedSubtotal = subtotal - discount;
        const fee = (discountedSubtotal + shippingCost) * (feePercentage / 100);
        const total = discountedSubtotal + shippingCost + fee;

        document.getElementById('summaryFee').textContent = `$${Math.round(fee).toLocaleString('es-CL')}`;
        document.getElementById('summaryTotal').textContent = `$${Math.round(total).toLocaleString('es-CL')}`;
    }

    async function applyCoupon() {
        const code = document.getElementById('couponInput').value.trim().toUpperCase();
        const messageEl = document.getElementById('couponMessage');
        const btn = document.getElementById('btnApplyCoupon');

        if (!code) {
            showCouponMessage(messageEl, 'Ingresa un código de cupón.', 'danger');
            return;
        }

        const cart = JSON.parse(localStorage.getItem('cart') || '[]');
        const subtotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);

        btn.disabled = true;
        btn.textContent = '...';

        try {
            const response = await fetch('/carrito/validate-coupon/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
                body: JSON.stringify({ code, subtotal })
            });
            const data = await response.json();

            if (data.valid) {
                appliedCoupon = { code, discount: data.discount };
                showCouponMessage(messageEl, data.message, 'success');

                const discountRow = document.getElementById('discountRow');
                discountRow.classList.remove('d-none');
                document.getElementById('discountLabel').textContent = data.label + ':';
                document.getElementById('summaryDiscount').textContent = `-$${Math.round(data.discount).toLocaleString('es-CL')}`;

                btn.textContent = 'Aplicado ✓';
                btn.classList.replace('btn-outline-secondary', 'btn-success');
                document.getElementById('couponInput').disabled = true;
            } else {
                appliedCoupon = null;
                showCouponMessage(messageEl, data.message, 'danger');
                btn.disabled = false;
                btn.textContent = 'Aplicar';
            }
        } catch (e) {
            showCouponMessage(messageEl, 'Error al validar el cupón.', 'danger');
            btn.disabled = false;
            btn.textContent = 'Aplicar';
        }

        updatePaymentFee();
    }
    
    async function createOrder() {
        const cart = JSON.parse(localStorage.getItem('cart') || '[]');
        
        if (cart.length === 0) {
            alert('Tu carrito está vacío');
            return;
        }
        
        // Preparar datos de envío
        const shippingInfo = {
            name: document.getElementById('name').value,
            email: document.getElementById('email').value,
            phone: document.getElementById('phone').value,
            address: document.getElementById('address').value,
            city: document.getElementById('city').value,
            region: document.getElementById('region').value,
            postal_code: document.getElementById('postal_code').value,
            notes: document.getElementById('notes').value
        };
        
        const selectedGateway = document.querySelector('input[name="payment_gateway"]:checked').value;
        
        // Mostrar modal de procesamiento
        if (!processingModal) {
            processingModal = new bootstrap.Modal(document.getElementById('processingModal'));
        }
        processingModal.show();
        btnProcessOrder.disabled = true;
        
        const csrfToken = getCsrfToken();
        if (!csrfToken) {
            processingModal.hide();
            btnProcessOrder.disabled = false;
            alert('No se encontró el token de seguridad (CSRF). Recarga la página e inténtalo de nuevo.');
            return;
        }

        try {
            const response = await fetch('/carrito/create-order/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    cart_items: cart,
                    shipping_info: shippingInfo,
                    payment_gateway: selectedGateway,
                    coupon_code: appliedCoupon ? appliedCoupon.code : ''
                })
            });
            
            const contentType = response.headers.get('content-type') || '';
            let data;
            if (contentType.includes('application/json')) {
                data = await response.json();
            } else {
                const text = await response.text();
                throw new Error('El servidor no devolvió JSON (código ' + response.status + '). ¿Sesión o CSRF?');
            }

            if (data.success) {
                // Redirigir a la página de pago
                window.location.href = data.payment_url;
            } else {
                processingModal.hide();
                btnProcessOrder.disabled = false;
                alert('Error: ' + (data.error || 'No se pudo crear la orden'));
            }
        } catch (error) {
            processingModal.hide();
            btnProcessOrder.disabled = false;
            alert('Error al procesar la orden: ' + error.message);
        }
    }

    function showCouponMessage(el, message, type) {
        el.className = `alert alert-${type} mt-2 py-2`;
        el.textContent = message;
        el.classList.remove('d-none');
    }

    function getCsrfToken() {
        const input = document.querySelector('[name=csrfmiddlewaretoken]');
        if (input && input.value) {
            return input.value;
        }
        return getCookie('csrftoken');
    }
    
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
