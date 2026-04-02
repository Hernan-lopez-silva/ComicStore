from django.shortcuts import render


def handler404(request, exception):
    """Página personalizada para errores 404 (se usa con DEBUG=False o al resolver rutas inexistentes)."""
    return render(request, '404.html', status=404)


def preview_404(request):
    """Vista previa de la página 404 en desarrollo (mismo diseño, HTTP 200)."""
    return render(request, '404.html', status=200)
