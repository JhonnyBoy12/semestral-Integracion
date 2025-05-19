from django.shortcuts import redirect, get_object_or_404, render
from herramientas.models import Herramienta
from .carrito import Carrito
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db import transaction
from ordenes.models import Orden, ItemOrden
from django.contrib import messages

import stripe
import requests 

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

    # Tasas de cambio fijas (de CLP a otras monedas)
    tasas_cambio = {
        'CLP': 1,
        'USD': 0.0012,
        'EUR': 0.0011,
        'JPY': 0.15,
        'PEN': 0.004,
    }

    # Obtener moneda seleccionada, por defecto CLP
    moneda = request.GET.get('moneda', 'CLP').upper()
    if moneda not in tasas_cambio:
        moneda = 'CLP'  # fallback en caso no exista la moneda
    request.session['moneda'] = moneda

    tasa = tasas_cambio[moneda]
    total_convertido = total * tasa
    
    carrito_convertido = {}
    for key, item in carrito.items():
        item_copiado = item.copy()
        if moneda == 'CLP':
            item_copiado['precio_convertido'] = item['precio']  # sin conversión
        else:
            item_copiado['precio_convertido'] = item['precio'] * tasa
        carrito_convertido[key] = item_copiado

    if moneda == 'CLP':
        total_convertido = total
    else:
        total_convertido = total * tasa
        
    context = {
        'carrito': carrito_convertido,
        'total': total,
        'moneda': moneda,
        'tasa': tasa,
        'total_convertido': round(total_convertido, 2)
    }
    return render(request, 'carrito/carrito.html', context)


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
    items = request.session.get('carrito', {})
    if not items:
        return render(request, 'carrito/error.html', {'message': 'El carrito está vacío'})

    moneda = request.session.get('moneda', 'CLP').lower()
    monedas_permitidas = ['clp', 'usd', 'eur', 'jpy', 'pen']

    if moneda not in monedas_permitidas:
        moneda = 'clp'

    tasas_cambio = {
        'clp': 1,
        'usd': 0.0012,
        'eur': 0.0011,
        'jpy': 0.15,
        'pen': 0.004,
    }

    tasa = tasas_cambio.get(moneda, 1)
    total_clp = sum(item['precio'] * item['cantidad'] for item in items.values())
    total_convertido = total_clp * tasa

    monedas_sin_decimales = ['jpy']

    if moneda in monedas_sin_decimales:
        unit_amount = int(round(total_convertido))
    else:
        unit_amount = int(round(total_convertido * 100))

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': moneda,
                    'product_data': {
                        'name': 'Compra en Ferremas',
                    },
                    'unit_amount': unit_amount,
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
