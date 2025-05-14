from django.shortcuts import render
from .models import Herramienta

# Crea tus vistas aqui.

##Vista inicial prueba de traer todos los datos de herramientas
def home(request):
    herramientas = Herramienta.objects.all()
    for herramienta in herramientas:
        herramienta.precio_clp = "{:,}".format(herramienta.precio)
    context ={"herramientas":herramientas }
    return render(request, "herramientas/home.html",context)

