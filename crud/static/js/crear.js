document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form');

    const camposRequeridos = [
        { id: 'id_title',       mensaje: 'El título es obligatorio.' },
        { id: 'id_description', mensaje: 'La descripción es obligatoria.' },
        { id: 'id_img_path',    mensaje: 'La ruta de la imagen es obligatoria.' },
        { id: 'id_price',       mensaje: 'El precio es obligatorio.' },
    ];

    camposRequeridos.forEach(function (campo) {
        const input = document.getElementById(campo.id);
        if (!input) return;
        input.addEventListener('input', function () {
            if (input.value.trim() !== '') {
                const error = document.getElementById(campo.id + '_error');
                if (error) error.style.display = 'none';
                input.classList.remove('input-invalido');
            }
        });
    });

    form.addEventListener('submit', function (e) {
        let hayErrores = false;

        camposRequeridos.forEach(function (campo) {
            const input = document.getElementById(campo.id);
            const error = document.getElementById(campo.id + '_error');
            if (!input || !error) return;

            if (input.value.trim() === '') {
                error.textContent = campo.mensaje;
                error.style.display = 'block';
                input.classList.add('input-invalido');
                hayErrores = true;
            } else {
                error.style.display = 'none';
                input.classList.remove('input-invalido');
            }
        });

        // Validar precio no negativo
        const precioInput = document.getElementById('id_price');
        const precioError = document.getElementById('id_price_error');
        if (precioInput && precioError && precioInput.value.trim() !== '') {
            if (parseFloat(precioInput.value) < 0) {
                precioError.textContent = 'El precio no puede ser un valor negativo.';
                precioError.style.display = 'block';
                precioInput.classList.add('input-invalido');
                hayErrores = true;
            }
        }

        if (hayErrores) {
            e.preventDefault();
        }
    });
});
