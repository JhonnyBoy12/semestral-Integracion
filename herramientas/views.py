from django.shortcuts import render, get_object_or_404
from .models import Herramienta

# Crea tus vistas aqui.

##Vista inicial prueba de traer todos los datos de herramientas
def home(request):
    herramientas = Herramienta.objects.all()
    for herramienta in herramientas:
        herramienta.precio_clp = "{:,}".format(herramienta.precio)
    context ={"herramientas":herramientas }
    return render(request, "herramientas/home.html",context)

def herramienta_detalles(request, herramienta_id):
    herramienta = get_object_or_404(Herramienta, pk=herramienta_id)
    return render(request, 'herramientas/detalleHerramientas.html', {'herramienta': herramienta})


