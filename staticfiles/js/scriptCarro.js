document.addEventListener('DOMContentLoaded', function () {

    var listaCarrito = JSON.parse(localStorage.getItem('cart'));

    showCart();

    // Verificar si hay items en el carrito para habilitar/deshabilitar el botón
    const btnCheckout = document.getElementById('btnCheckout');
    if (btnCheckout && (!listaCarrito || listaCarrito.length === 0)) {
        btnCheckout.classList.add('disabled');
        btnCheckout.style.pointerEvents = 'none';
    }
    
    document.addEventListener('click', function (e) {
        if (e.target && e.target.matches('.fa-trash-can')) {
            let idBorrar = parseInt(e.target.id);
            listaCarrito = listaCarrito.filter(item => item.id !== idBorrar);
            localStorage.setItem('cart', JSON.stringify(listaCarrito));
            //console.log(listaCarrito);
            this.location.reload();
        }
    });

    window.addEventListener('scroll', function () {
        const supermanIcon = document.getElementById('scroll-top-icon');
        if (window.scrollY > 30) {
            supermanIcon.style.display = 'block';
        } else {
            supermanIcon.style.display = 'none';
        }
    });

    

    //Función para mostrar el contenido del carrito
    function showCart() {
        const totalCarrito = document.getElementById('totalCarrito');
        const tabla = document.getElementById('tabla');
        const mensajeCarritoVacio = document.getElementById('mensajeCarritoVacio'); // Asegúrate de tener este elemento en tu HTML
    
        let total = 0;

        if (listaCarrito.length === 0) {
            tabla.style.display = 'none'; // Oculta la tabla
            mensajeCarritoVacio.style.display = 'block'; // Muestra el mensaje de carrito vacío
            mensajeCarritoVacio.innerHTML = '<h2>Tu carrito está vacío</h2>'; // Asegúrate de que este mensaje se ajuste a tu HTML
        } else {
            
            mensajeCarritoVacio.style.display = 'none'; // Oculta el mensaje de carrito vacío
            const tituloCarro = document.getElementById('tituloCarro');
            if(listaCarrito.length === 1){
                tituloCarro.innerHTML = `<h2>Carrito de compras (${listaCarrito.length} producto)</h2>`;
            }else{
                tituloCarro.innerHTML = `<h2>Carrito de compras (${listaCarrito.length} productos)</h2>`;
            }
            listaCarrito.forEach(element => {
                mostrarCarrito.innerHTML += `<tr class="align-middle">
                                                <td><i id=${element.id} class="fa-regular fa-trash-can fa-2x"></i></td>
                                                <td><img class="thumbnail" src="${element.img}" alt=""></td>
                                                <td>${element.id}</td>
                                                <td>${element.title}</td>
                                                <td>$${element.price}</td>
                                                <td>${element.quantity}</td>
                                                <td>$${element.quantity * element.price}</td>                                                       
                                            </tr>`;
                total += element.quantity * element.price;
            });
    
            totalCarrito.innerHTML = `$${total}`      ;
        }
    };

});



