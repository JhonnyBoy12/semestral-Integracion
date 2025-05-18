from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from herramientas.models import Herramienta, Categoria
from django.contrib.auth.models import User
from ordenes.models import Orden
from .forms import HerramientaForm
from autenticacion.decorators import bodeguero_required


@login_required
@bodeguero_required
def ver_usuarios_y_ordenes(request):
    # Solo verificamos el rol (el middleware ya verifica el acceso)
    usuarios = User.objects.prefetch_related('orden_set__items')
    herramientas = Herramienta.objects.all()

    for herramienta in herramientas:
        herramienta.precio_clp = "{:,}".format(herramienta.precio)

    context = {
        'usuarios': usuarios,
        'herramientas': herramientas,
    }
    return render(request, 'bodeguero/bodeguero.html', context)


## FUNCION CONSULTA DE STOCK BASE DE DATOS
@login_required
@bodeguero_required
def consultarStock(request, herramienta_id):
    herramienta = get_object_or_404(Herramienta, pk=herramienta_id)
    return render(request, 'bodeguero/mostrar_stock.html', {'herramienta': herramienta})

## FUNCION AUMENTA STOCK DATO DE HERRAMIENTA SEGUN ID DE HERRAMIENTA
@login_required
@bodeguero_required
@require_http_methods(["POST"])  # Solo acepta POST
def aumentarStock(request, herramienta_id): 
    herramienta = get_object_or_404(Herramienta, pk=herramienta_id)
    herramienta.cantidad += 1
    herramienta.save()
    return redirect('mostrar_stock', herramienta_id=herramienta_id)

## FUNCION AGREGA HERRAMIENTRA MEDIANTE METODO POST
@login_required
@bodeguero_required
def agregarHerramienta(request):
    if request.method == 'POST':
        form = HerramientaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('bodeguero')
    else:
        form = HerramientaForm()
    
    return render(request, 'bodeguero/agregarHerramienta.html', {'form': form})

## FUNCION EDITA DATOS DE HERRAMIENTA MEDIANTE METODO POST
@login_required
@bodeguero_required
def editarHerramienta(request, herramienta_id):
    herramienta = get_object_or_404(Herramienta, pk=herramienta_id)

    if request.method == 'POST':
        herramienta.nombre = request.POST.get('nombre')
        herramienta.precio = request.POST.get('precio')
        herramienta.cantidad = request.POST.get('cantidad')

        if 'imagen' in request.FILES:
            herramienta.imagen = request.FILES['imagen']

        herramienta.save()
        return redirect('mostrar_stock', herramienta_id=herramienta.id)
    else:
        categorias = Categoria.objects.all()
        return render(request, 'bodeguero/editar_herramienta.html', {
            'herramienta': herramienta,
        })