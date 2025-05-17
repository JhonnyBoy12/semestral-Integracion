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


@login_required
def procesar_compra(request):
    carrito = Carrito(request)

    if request.method == 'POST':
        if not carrito.carro:
            messages.error(request, "El carrito está vacío.")
            return redirect("carrito:ver_carrito")  # Ajusta este nombre según tu URL

        total = 0
        cantidad_total = 0

        try:
            with transaction.atomic():
                # Verifica stock y prepara datos
                for key, item in carrito.carro.items():
                    herramienta = Herramienta.objects.get(id=key)

                    if herramienta.cantidad < item['cantidad']:
                        messages.error(request, f"No hay suficiente stock para {herramienta.nombre}.")
                        return redirect("carrito:ver_carrito")

                    total += item['precio'] * item['cantidad']
                    cantidad_total += item['cantidad']

                # Crear orden
                orden = Orden.objects.create(
                    usuario=request.user,
                    total_precio=total,
                    cantidad_herramientas=cantidad_total
                )

                # Crear ítems y actualizar stock
                for key, item in carrito.carro.items():
                    herramienta = Herramienta.objects.get(id=key)

                    ItemOrden.objects.create(
                        orden=orden,
                        herramienta=herramienta,
                        cantidad=item['cantidad'],
                        precio=item['precio']
                    )

                    herramienta.cantidad -= item['cantidad']
                    herramienta.save()

                carrito.limpiar()
                messages.success(request, "Compra realizada exitosamente.")
                return redirect("misPedidos")  # Ajusta a la URL de tus pedidos

        except Exception as e:
            messages.error(request, f"Ocurrió un error: {str(e)}")
            return redirect("home")

    # Si no es POST
    return render(request, 'ordenes/misPedidos.html', {'carrito': carrito})