from django import forms
from herramientas.models import Herramienta

class HerramientaForm(forms.ModelForm):
    class Meta:
        model = Herramienta
        fields = ['nombre', 'id_categoria', 'precio', 'descripcion', 'imagen', 'cantidad']
        widgets = {
            'descripcion': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Descripción de la herramienta',
            }),
            'imagen': forms.ClearableFileInput(attrs={
                'accept': 'image/*'
            }),
        }
