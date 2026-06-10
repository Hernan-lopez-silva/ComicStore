document.addEventListener('DOMContentLoaded', function () {

    var listaCarrito = JSON.parse(localStorage.getItem('cart')) || [];

    showCart();

    document.querySelectorAll('.btnClose').forEach(function(element) {
        element.addEventListener('click', function () {
            hideModal(element);
        });
    });

    document.addEventListener('click', function (e) {
        if (e.target && e.target.matches('.fa-trash-can')) {
            var idBorrar = parseInt(e.target.id);
            listaCarrito = listaCarrito.filter(function(item) { return item.id !== idBorrar; });
            localStorage.setItem('cart', JSON.stringify(listaCarrito));
            window.location.reload();
        }

        if (e.target && e.target.matches('.btn-incrementar')) {
            var id = parseInt(e.target.dataset.id);
            var item = listaCarrito.find(function(i) { return i.id === id; });
            if (item) {
                item.quantity += 1;
                localStorage.setItem('cart', JSON.stringify(listaCarrito));
                actualizarFila(id);
            }
        }

        if (e.target && e.target.matches('.btn-decrementar')) {
            var id = parseInt(e.target.dataset.id);
            var item = listaCarrito.find(function(i) { return i.id === id; });
            if (item) {
                if (item.quantity > 1) {
                    item.quantity -= 1;
                    localStorage.setItem('cart', JSON.stringify(listaCarrito));
                    actualizarFila(id);
                } else {
                    listaCarrito = listaCarrito.filter(function(i) { return i.id !== id; });
                    localStorage.setItem('cart', JSON.stringify(listaCarrito));
                    window.location.reload();
                }
            }
        }
    });

    function actualizarFila(id) {
        var item = listaCarrito.find(function(i) { return i.id === id; });
        var btn = document.querySelector('.btn-incrementar[data-id="' + id + '"]');
        var fila = btn.closest('tr');
        fila.querySelector('.cantidad-item').textContent = item.quantity;
        fila.querySelector('.subtotal-item').textContent = '$' + (item.quantity * item.price).toLocaleString('es-CL');
        var total = listaCarrito.reduce(function(acc, i) { return acc + i.quantity * i.price; }, 0);
        document.getElementById('totalCarrito').innerHTML = '$' + total.toLocaleString('es-CL');
    }

    window.addEventListener('scroll', function () {
        var supermanIcon = document.getElementById('scroll-top-icon');
        if (window.scrollY > 30) {
            supermanIcon.style.display = 'block';
        } else {
            supermanIcon.style.display = 'none';
        }
    });

    function showCart() {
        var totalCarrito = document.getElementById('totalCarrito');
        var tabla = document.getElementById('tabla');
        var mensajeCarritoVacio = document.getElementById('mensajeCarritoVacio');
        var total = 0;

        if (listaCarrito.length === 0) {
            tabla.style.display = 'none';
            mensajeCarritoVacio.style.display = 'block';
            mensajeCarritoVacio.innerHTML = '<h2>Tu carrito esta vacio</h2>';
        } else {
            mensajeCarritoVacio.style.display = 'none';
            var tituloCarro = document.getElementById('tituloCarro');
            if (listaCarrito.length === 1) {
                tituloCarro.innerHTML = '<h2>Carrito de compras (' + listaCarrito.length + ' producto)</h2>';
            } else {
                tituloCarro.innerHTML = '<h2>Carrito de compras (' + listaCarrito.length + ' productos)</h2>';
            }

            var tbody = document.getElementById('mostrarCarrito');
            listaCarrito.forEach(function(element) {
                var fila = document.createElement('tr');
                fila.className = 'align-middle';
                fila.innerHTML = '<td><i id="' + element.id + '" class="fa-regular fa-trash-can fa-2x"></i></td>'
                    + '<td><img class="thumbnail" src="' + element.img + '" alt=""></td>'
                    + '<td>' + element.id + '</td>'
                    + '<td>' + element.title + '</td>'
                    + '<td>$' + Number(element.price).toLocaleString('es-CL') + '</td>'
                    + '<td><div class="d-flex align-items-center justify-content-center gap-2">'
                    + '<button class="btn btn-sm btn-outline-secondary btn-decrementar" data-id="' + element.id + '">-</button>'
                    + '<span class="cantidad-item">' + element.quantity + '</span>'
                    + '<button class="btn btn-sm btn-outline-secondary btn-incrementar" data-id="' + element.id + '">+</button>'
                    + '</div></td>'
                    + '<td class="subtotal-item">$' + (element.quantity * element.price).toLocaleString('es-CL') + '</td>';
                tbody.appendChild(fila);
                total += element.quantity * element.price;
            });

            totalCarrito.innerHTML = '$' + total.toLocaleString('es-CL');
        }
    }

    function showModal() {
        var modal = document.getElementById('modalPago');
        if (!modal) return;
        modal.classList.add('show');
        modal.style.display = 'block';
        document.body.classList.add('modal-open');
        document.body.style.paddingRight = '17px';
    }

    function hideModal(button) {
        var modal = button.closest('.modal');
        if (modal) {
            modal.classList.remove('show');
            modal.style.display = 'none';
            document.body.classList.remove('modal-open');
            document.body.style.paddingRight = '0';
        }
    }

});
