from django import template

register = template.Library()


@register.filter
def punto_miles(value):
    """Formatea un número con punto como separador de miles (formato chileno).
    Ejemplo: 12500 → '12.500'
    """
    try:
        num = float(value)
        entero = int(round(num))
        return f"{entero:,}".replace(",", ".")
    except (ValueError, TypeError):
        return value
