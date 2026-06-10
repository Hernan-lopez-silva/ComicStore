from django import forms
from .models import Comic

MENSAJE_OBLIGATORIO = 'Este campo es obligatorio.'

class FormComic(forms.ModelForm):
    description = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 6,
            'placeholder': 'Sinopsis o detalle del cómic para la ficha de producto',
        }),
        label='Descripción',
        error_messages={'required': MENSAJE_OBLIGATORIO},
    )

    class Meta:
        model = Comic
        fields = ['title', 'description', 'img_path', 'price']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'img_path': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': 'Título',
            'img_path': 'Ruta de la Imagen',
            'price': 'Precio',
        }
        error_messages = {
            'title':    {'required': MENSAJE_OBLIGATORIO},
            'img_path': {'required': MENSAJE_OBLIGATORIO},
            'price':    {'required': MENSAJE_OBLIGATORIO},
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise forms.ValidationError('El precio no puede ser un valor negativo.')
        return price

