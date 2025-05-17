from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from ordenes.models import Orden, ItemOrden
from herramientas.models import Herramienta
from django.contrib import messages
from carrito.carrito import Carrito
from django.db import transaction

@login_required
def mis_pedidos(request):
    pedidos = Orden.objects.filter(usuario=request.user)
    context = {
        'pedidos': pedidos
    }
    return render(request, 'ordenes/misPedidos.html', context)




