from django.shortcuts import render, get_object_or_404, redirect
from herramientas.models import Herramienta, Categoria
from django.contrib.auth.models import User
from ordenes.models import Orden
from django.http import HttpResponse
from .forms import HerramientaForm
# Create your views here.



def ver_usuarios_y_ordenes(request):
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
def consultarStock(request, herramienta_id): ##Web Service de Consultar Stock
    herramienta = get_object_or_404(Herramienta, pk=herramienta_id )
    return render(request, 'bodeguero/mostrar_stock.html', {'herramienta' : herramienta})

## FUNCION AUMENTA STOCK DATO DE HERRAMIENTA SEGUN ID DE HERRAMIENTA
def aumentarStock(request, herramienta_id): 
    herramienta = get_object_or_404(Herramienta, pk=herramienta_id)
    if request.method == "POST":
        herramienta.cantidad+= 1
        herramienta.save()
        return redirect('mostrar_stock', herramienta_id=herramienta_id)
    return HttpResponse("Error", status=405)

## FUNCION AGREGA HERRAMIENTRA MEDIANTE METODO POST
def agregarHerramienta(request):
    if request.method == 'POST':
        form = HerramientaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('bodeguero')
    else:
        form=HerramientaForm()
    return render(request, 'bodeguero/agregarHerramienta.html', {'form':form})

## FUNCION EDITA DATOS DE HERRAMIENTA MEDIANTE METODO POST
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
