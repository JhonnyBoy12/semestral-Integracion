from django.db import models
from django import forms
from herramientas.models import Herramienta, Categoria


class HerramientaForm(forms.ModelForm):
    class Meta:
        model = Herramienta
        fields = [ 'nombre', 'id_categoria', 'precio', 'descripcion', 'imagen', 'cantidad']
        widgets= {
            'imagen': forms.ClearableFileInput(attrs={'accept':'image/*'}),
        }