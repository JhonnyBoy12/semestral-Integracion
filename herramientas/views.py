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

## WS FILTRA ID
def catalogo(request):
    query = request.GET.get('q')  # Texto del buscador
    orden = request.GET.get('orden')  # Parámetro de orden

    herramientas = Herramienta.objects.all()

    # Filtro por búsqueda
    if query:
        herramientas = herramientas.filter(nombre__icontains=query)

    # Ordenamiento
    if orden == 'nombre_asc':
        herramientas = herramientas.order_by('nombre')
    elif orden == 'nombre_desc':
        herramientas = herramientas.order_by('-nombre')
    elif orden == 'precio_asc':
        herramientas = herramientas.order_by('precio')
    elif orden == 'precio_desc':
        herramientas = herramientas.order_by('-precio')

    # Formatear el precio
    for herramienta in herramientas:
        herramienta.precio_clp = "{:,}".format(herramienta.precio)

    context = {
        "herramientas": herramientas,
        "query": query,
        "orden_actual": orden
    }
    return render(request, "herramientas/catalogo.html", context)
