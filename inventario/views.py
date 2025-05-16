from django.shortcuts import render, get_object_or_404, redirect
from herramientas.models import Herramienta, Categoria
from django.http import HttpResponse
from .forms import HerramientaForm
# Create your views here.

## VER HERRAMIENTAS
def verHerramientas(request):
    herramientas = Herramienta.objects.all()
    for herramienta in herramientas:
        herramienta.precio_clp = "{:,}".format(herramienta.precio)
    context ={"herramientas":herramientas }
    return render(request, 'bodeguero/bodeguero.html',{'herramientas' : herramientas})

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
