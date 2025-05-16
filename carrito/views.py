from django.shortcuts import redirect, get_object_or_404, render
from herramientas.models import Herramienta
import mercadopago
from django.contrib.auth.decorators import login_required
from django.conf import settings
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
    return redirect('home')

## FUNCION AUMENTA CANTIDAD DE UN PRODUCTO DEL CARRITO
def aumentar_cantidad(request, herramienta_id):
    carrito = request.session.get('carrito', {})

    if str(herramienta_id) in carrito:
        carrito[str(herramienta_id)]['cantidad'] += 1
        request.session['carrito'] = carrito

    return redirect('')

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

@login_required
def comprar(request):
    if not request.user.is_authenticated:
        return redirect('login')

    items = request.session.get('carrito', {})
    total = sum(item['precio'] * item['cantidad'] for item in items.values())

    if not items:
        return render(request, 'carrito/error.html', {'message': 'El carrito está vacío'})

    try:
        buy_order = f"orden-{request.user.id}-{request.session.session_key}"
        session_id = f"sesion-{request.user.id}"
        return_url = request.build_absolute_uri('/carrito/exito/')
        print("Return URL:", return_url)

        preference_data = {
            "items": [
                {
                    "title": "Compra en Ferremas",
                    "quantity": 1,
                    "unit_price": float(total),
                    "currency_id": "CLP"
                }
            ],
            "payer": {
                "name": request.user.username,
                "email": request.user.email
            },
            "back_urls": {
                "success": return_url,
                "failure": return_url,
                "pending": return_url
            },
            ##"auto_return": "all"
        }

        sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

        try:
            preference_response = sdk.preference().create(preference_data)
            print("Respuesta Mercado Pago:", preference_response)  # <--- Aquí
            preference = preference_response["response"]

            if 'init_point' not in preference:
                return render(request, 'carrito/error.html', {'message': 'No se pudo obtener el init_point de la preferencia de pago.'})

            return redirect(preference['init_point'])

        except Exception as e:
            return render(request, 'carrito/error.html', {'message': f'Error en Mercado Pago: {str(e)}'})

    except Exception as e:
        return render(request, 'carrito/error.html', {'message': f'Error al generar la orden: {str(e)}'})

def exito(request):
    # Aquí puedes vaciar carrito o mostrar info
    request.session['carrito'] = {}
    return render(request, 'carrito/exito.html')

def fallo(request):
    return render(request, 'carrito/fallo.html')

def pendiente(request):
    return render(request, 'carrito/pendiente.html')

