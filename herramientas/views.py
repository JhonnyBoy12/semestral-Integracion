import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Herramienta
from django.db.models.functions import Lower

# Vista inicial prueba de traer todos los datos de herramientas
def home(request):
    herramientas = Herramienta.objects.all()
    
    # Verificar si es JSON
    if request.content_type == 'application/json':
        # Serializar las herramientas a JSON
        herramientas_list = []
        for herramienta in herramientas:
            herramientas_list.append({
                'id': herramienta.id,
                'nombre': herramienta.nombre,
                'descripcion': herramienta.descripcion,
                'precio': float(herramienta.precio),  # Convertir a float para JSON
                'stock': herramienta.cantidad,
                'imagen': request.build_absolute_uri(herramienta.imagen.url) if herramienta.imagen else None,
            })
        return JsonResponse({'herramientas': herramientas_list}, safe=False)
    else:
        # Formatear para HTML
        for herramienta in herramientas:
            herramienta.precio_clp = "{:,}".format(herramienta.precio)
        context = {"herramientas": herramientas}
        return render(request, "herramientas/home.html", context)

def herramienta_detalles(request, herramienta_id):
    herramienta = get_object_or_404(Herramienta, pk=herramienta_id)
    
    # Verificar si es JSON
    if request.content_type == 'application/json':
        # Construir JSON para el detalle
        data = {
            'id': herramienta.id,
            'nombre': herramienta.nombre,
            'descripcion': herramienta.descripcion,
            'precio': float(herramienta.precio),
            'stock': herramienta.cantidad,
            'imagen': request.build_absolute_uri(herramienta.imagen.url) if herramienta.imagen else None,
        }
        return JsonResponse(data)
    else:
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
        herramientas = herramientas.order_by(Lower('nombre'))
    elif orden == 'nombre_desc':
        herramientas = herramientas.order_by(Lower('nombre').desc())
    elif orden == 'precio_asc':
        herramientas = herramientas.order_by('precio')
    elif orden == 'precio_desc':
        herramientas = herramientas.order_by('-precio')

    # Verificar si es JSON
    if request.content_type == 'application/json':
        # Serializar para JSON
        herramientas_list = []
        for herramienta in herramientas:
            herramientas_list.append({
                'id': herramienta.id,
                'nombre': herramienta.nombre,
                'precio': float(herramienta.precio),
                'stock': herramienta.cantidad,
                'imagen': request.build_absolute_uri(herramienta.imagen.url) if herramienta.imagen else None,
            })
        return JsonResponse({
            'herramientas': herramientas_list,
            'query': query,
            'orden_actual': orden
        }, safe=False)
    else:
        # Formatear para HTML
        for herramienta in herramientas:
            herramienta.precio_clp = "{:,}".format(herramienta.precio)
        context = {
            "herramientas": herramientas,
            "query": query,
            "orden_actual": orden
        }
        return render(request, "herramientas/catalogo.html", context)
