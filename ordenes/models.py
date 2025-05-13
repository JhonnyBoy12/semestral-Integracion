from django.db import models
from django.contrib.auth.models import User
from herramientas.models import Herramienta

# Create your models here.
class Orden(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    total_precio = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_herramientas = models.IntegerField()
    fehca = models.DateTimeField(auto_now_add=True)

    def __str__(self): ##devuelve cadena con el campo id y username
        return f"Orden {self.id} de {self.usuario.username}" 

    @property
    def total(self):
        return sum(item.precio_total for item in self.items.all())

class ItemOrden(models.Model):
    orden = models.ForeignKey(Orden, related_name='items', on_delete=models.CASCADE)
    herramienta = models.ForeignKey(Herramienta, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.cantidad} x {self.herramienta.nombre}"

    @property
    def precio_total(self):
        return self.cantidad * self.precio