from django import forms
from .models import Comic

class FormComic(forms.ModelForm):
    class Meta:
        model = Comic
        fields = ['title', 'description', 'img_path', 'price']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Sinopsis o detalle del cómic para la ficha de producto',
            }),
            'img_path': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': 'Título',
            'description': 'Descripción',
            'img_path': 'Ruta de la Imagen',
            'price': 'Precio',
        }

