from django.shortcuts import redirect, get_object_or_404, render
from herramientas.models import Herramienta
from .carrito import Carrito
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db import transaction
from ordenes.models import Orden, ItemOrden
from django.contrib import messages

import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

## FUNCION AGREGA PRODUCTO A CARRITO
def agregar_al_carrito(request, herramienta_id):
    herramienta = get_object_or_404(Herramienta, pk=herramienta_id)

    carrito = request.session.get('carrito', {})

    if str(herramienta_id) in carrito:
        carrito[str(herramienta_id)]['cantidad'] += 1
    else:
        carrito[str(herramienta_id)] = {
            'nombre': herramienta.nombre,
            'precio': float(herramienta.precio),
            'imagen': herramienta.imagen.url if herramienta.imagen else '',
            'cantidad': 1,
        }

    request.session['carrito'] = carrito
    return redirect('catalogo')

## FUNCION AUMENTA CANTIDAD DE UN PRODUCTO DEL CARRITO
def aumentar_cantidad(request, herramienta_id):
    carrito = request.session.get('carrito', {})

    if str(herramienta_id) in carrito:
        carrito[str(herramienta_id)]['cantidad'] += 1
        request.session['carrito'] = carrito

    return redirect('carrito')

## FUNCION DISMINUYE CANTIDAD DE UN PRODUCTO DEL CARRITO
def disminuir_cantidad(request, herramienta_id):
    carrito = request.session.get('carrito', {})

    if str(herramienta_id) in carrito:
        if carrito[str(herramienta_id)]['cantidad'] > 1:
            carrito[str(herramienta_id)]['cantidad'] -= 1
        else:
            del carrito[str(herramienta_id)]
        request.session['carrito'] = carrito

    return redirect('carrito')

## FUNCION ELIMINAR UN PRODUCTO DEL CARRITO
def eliminar_producto(request, herramienta_id):
    carrito = request.session.get('carrito', {})

    if str(herramienta_id) in carrito:
        del carrito[str(herramienta_id)]
        request.session['carrito'] = carrito

    return redirect('carrito')

## FUNCION VACIA PRODUCTOS DEL CARIRITO
def vaciar_carrito(request):
    request.session['carrito'] = {}
    return redirect('carrito')

## FUNCION MUESTRA CARRITO TEMPLATE Y CANTIDAD TOTAL DEL ORDEN
def ver_carrito(request):
    carrito = request.session.get('carrito', {})
    total = sum(item['precio'] * item['cantidad'] for item in carrito.values())
    return render(request, 'carrito/carrito.html', {'carrito': carrito, 'total': total})


def exito(request):
    carrito = Carrito(request)

    if not carrito.carro:
        return render(request, 'carrito/exito.html', {'mensaje': "El carrito ya fue procesado o está vacío."})

    total = 0
    cantidad_total = 0

    try:
        with transaction.atomic():
            for key, item in carrito.carro.items():
                herramienta = Herramienta.objects.get(id=key)

                if herramienta.cantidad < item['cantidad']:
                    messages.error(request, f"No hay suficiente stock para {herramienta.nombre}.")
                    return redirect("carrito:ver_carrito")

                total += item['precio'] * item['cantidad']
                cantidad_total += item['cantidad']

            orden = Orden.objects.create(
                usuario=request.user,
                total_precio=total,
                cantidad_herramientas=cantidad_total
            )

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

        return render(request, 'carrito/exito.html', {'mensaje': "Compra procesada exitosamente."})

    except Exception as e:
        messages.error(request, f"Ocurrió un error al procesar la compra: {str(e)}")
        return redirect("home")


def fallo(request):
    return render(request, 'carrito/fallo.html')


@login_required
def comprar(request):
    carrito = Carrito(request)
    items = request.session.get('carrito', {})
    total = sum(item['precio'] * item['cantidad'] for item in items.values())

    if not items:
        return render(request, 'carrito/error.html', {'message': 'El carrito está vacío'})

    try:
        # Crear la sesión de pago de Stripe
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'clp',
                    'product_data': {
                        'name': 'Compra en Ferremas',
                    },
                    'unit_amount': int(total), 
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri('/carrito/exito/'),
            cancel_url=request.build_absolute_uri('/carrito/fallo/'),
        )
        return redirect(session.url, code=303)

    except stripe.error.CardError:
        return render(request, 'carrito/error.html', {'message': 'Error al procesar el pago con Stripe.'})

