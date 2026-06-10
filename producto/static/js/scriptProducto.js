document.addEventListener('DOMContentLoaded', () => {

    const btnLoginRequerido = document.getElementById('btnLoginRequerido');
    if (btnLoginRequerido) {
        btnLoginRequerido.addEventListener('click', showModalLogin);
    }

    const btnCarro = document.getElementById('carro');
    if (btnCarro) {
        btnCarro.addEventListener('click', function () {
            const titulo = document.getElementById('titleComic').innerText;
            const id = parseInt(document.getElementById('idComic').innerText.split(' ')[1]);
            const precio = parseInt(document.getElementById('priceComic').innerText.split('$')[1].replace(/\./g, ''));
            const estado = document.getElementById('statusComic').innerText.split(' ')[1];
            const cantidad = document.getElementById('cantidadInput').value;
            const img = document.getElementById('imgComic').getAttribute('src');

            if (estado === 'Disponible') {
                addToCart(id, titulo, precio, img, cantidad);
                showModal();
            } else {
                showModalAgotado();
            }
        });
    }

    document.querySelectorAll('.btnClose').forEach(element => {
        element.addEventListener('click', function () {
            hideModal(element);
        });
    });

    document.getElementById("btnMas").addEventListener("click", function () {
        var cantidadInput = document.getElementById("cantidadInput");
        cantidadInput.value = parseInt(cantidadInput.value) + 1;
    });

    document.getElementById("btnMenos").addEventListener("click", function () {
        var cantidadInput = document.getElementById("cantidadInput");
        cantidadInput.value = Math.max(parseInt(cantidadInput.value) - 1, 1);
    });

    window.addEventListener('scroll', function () {
        const supermanIcon = document.getElementById('scroll-top-icon');
        if (window.scrollY > 30) {
            supermanIcon.style.display = 'block';
        } else {
            supermanIcon.style.display = 'none';
        }
    });

    function showModal() {
        const modal = document.getElementById('exampleModal');
        modal.classList.add('show');
        modal.style.display = 'block';
        document.body.classList.add('modal-open');
        document.body.style.paddingRight = '17px';
    }

    function showModalLogin() {
        const modal = document.getElementById('modalLoginRequerido');
        modal.classList.add('show');
        modal.style.display = 'block';
        document.body.classList.add('modal-open');
        document.body.style.paddingRight = '17px';
    }

    function showModalAgotado() {
        const modal = document.getElementById('modalAgotado');
        modal.classList.add('show');
        modal.style.display = 'block';
        document.body.classList.add('modal-open');
        document.body.style.paddingRight = '17px';
    }

    function hideModal(button) {
        const modal = button.closest('.modal');
        if (modal) {
            modal.classList.remove('show');
            modal.style.display = 'none';
            document.body.classList.remove('modal-open');
            document.body.style.paddingRight = '0';
        }
    }

    function addToCart(id, titulo, precio, img, cantidad) {
        let cart = JSON.parse(localStorage.getItem('cart')) || [];
        let comic = cart.find(item => item.id === id);
        let cantidadNumerica = parseInt(cantidad);

        if (comic) {
            comic.quantity += cantidadNumerica;
        } else {
            cart.push({ id: id, title: titulo, price: precio, img: img, quantity: cantidadNumerica });
        }

        localStorage.setItem('cart', JSON.stringify(cart));
    }

});
