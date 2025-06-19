from django.shortcuts import redirect, get_object_or_404, render
from herramientas.models import Herramienta
from .carrito import Carrito
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db import transaction
from ordenes.models import Orden, ItemOrden
from django.contrib import messages

import stripe
import json

stripe.api_key = settings.STRIPE_SECRET_KEY

## FUNCION AGREGA PRODUCTO A CARRITO
def agregar_al_carrito(request, herramienta_id):
    herramienta = get_object_or_404(Herramienta, pk=herramienta_id)
    is_json = request.content_type == 'application/json'
    
    # Obtener o inicializar el carrito
    carrito = request.session.get('carrito', {})
    
    herramienta_id_str = str(herramienta_id)
    
    if herramienta_id_str in carrito:
        carrito[herramienta_id_str]['cantidad'] += 1
    else:
        carrito[herramienta_id_str] = {
            'nombre': herramienta.nombre,
            'precio': float(herramienta.precio),
            'imagen': request.build_absolute_uri(herramienta.imagen.url) if herramienta.imagen else '',
            'cantidad': 1,
            'herramienta_id': herramienta_id,
        }

    request.session['carrito'] = carrito
    
    if is_json:
        # Calcular total
        total = sum(item['precio'] * item['cantidad'] for item in carrito.values())
        
        return JsonResponse({
            'success': 'Producto agregado al carrito',
            'carrito': carrito,
            'total': total,
            'item_actualizado': carrito[herramienta_id_str]
        })
    else:
        return redirect('catalogo')

## FUNCION AUMENTA CANTIDAD DE UN PRODUCTO DEL CARRITO
def aumentar_cantidad(request, herramienta_id):
    carrito = request.session.get('carrito', {})
    herramienta_id_str = str(herramienta_id)

    # Verificamos que el producto esté en el carrito
    if herramienta_id_str in carrito:
        herramienta = get_object_or_404(Herramienta, pk=herramienta_id)  # Solo si está en el carrito
        cantidad_actual = carrito[herramienta_id_str]['cantidad']

        if cantidad_actual < herramienta.stock:
            carrito[herramienta_id_str]['cantidad'] += 1
        else:
            messages.warning(request, "No hay más stock disponible para esta herramienta.")
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
    is_json = request.content_type == 'application/json'

    # Para respuestas JSON
    if is_json:
        total = sum(item['precio'] * item['cantidad'] for item in carrito.values())
        
        # Convertir a lista para mejor estructura en JSON
        carrito_list = []
        for key, item in carrito.items():
            item['id'] = key  # Agregar ID al item
            carrito_list.append(item)
        
        return JsonResponse({
            'carrito': carrito_list,
            'total': total,
            'count': len(carrito)
        })

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


@csrf_exempt
@login_required
def exito(request):
    is_json = request.content_type == 'application/json'
    carrito_data = {}
    
    # Manejo de solicitudes JSON para Postman
    if is_json:
        try:
            # Leer y parsear datos JSON
            data = json.loads(request.body)
            carrito_data = data.get('carrito', {})
            
            # Convertir lista a diccionario si es necesario
            if isinstance(carrito_data, list):
                carrito_dict = {}
                for item in carrito_data:
                    key = str(item['herramienta_id'])
                    carrito_dict[key] = {
                        'cantidad': int(item['cantidad']),
                        'precio': float(item['precio']),
                        'nombre': item.get('nombre', '')
                    }
                carrito_data = carrito_dict
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Formato JSON inválido'}, status=400)
        except KeyError as e:
            return JsonResponse({'error': f'Falta campo requerido: {str(e)}'}, status=400)
    else:
        # Comportamiento normal para la web
        carrito = Carrito(request)
        carrito_data = carrito.carro

    # Verificar si el carrito está vacío
    if not carrito_data:
        if is_json:
            return JsonResponse({'error': 'El carrito está vacío'}, status=400)
        else:
            return render(request, 'carrito/exito.html', {'mensaje': "El carrito ya fue procesado o está vacío."})

    total = 0
    cantidad_total = 0
    items_procesados = []

    try:
        with transaction.atomic():
            # Validar stock y calcular totales
            for key, item in carrito_data.items():
                herramienta_id = int(key)
                herramienta = Herramienta.objects.get(id=herramienta_id)
                cantidad = item['cantidad']
                
                # Verificar stock disponible
                if herramienta.cantidad < cantidad:
                    error_msg = f"No hay suficiente stock para {herramienta.nombre}."
                    if is_json:
                        return JsonResponse({'error': error_msg}, status=400)
                    else:
                        messages.error(request, error_msg)
                        return redirect("carrito:ver_carrito")

                # Calcular totales
                total += item['precio'] * cantidad
                cantidad_total += cantidad
                
                # Guardar detalles para respuesta
                items_procesados.append({
                    'herramienta_id': herramienta.id,
                    'nombre': herramienta.nombre,
                    'cantidad': cantidad,
                    'precio_unitario': item['precio'],
                    'subtotal': item['precio'] * cantidad
                })

            # Crear la orden en la base de datos
            orden = Orden.objects.create(
                usuario=request.user,
                total_precio=total,
                cantidad_herramientas=cantidad_total
            )

            # Crear items de la orden y actualizar stock
            for key, item in carrito_data.items():
                herramienta_id = int(key)
                herramienta = Herramienta.objects.get(id=herramienta_id)
                cantidad = item['cantidad']
                
                # Crear item de orden
                ItemOrden.objects.create(
                    orden=orden,
                    herramienta=herramienta,
                    cantidad=cantidad,
                    precio=item['precio']
                )

                # Actualizar stock
                herramienta.cantidad -= cantidad
                herramienta.save()

            # Limpiar carrito solo si es una solicitud web normal
            if not is_json:
                carrito = Carrito(request)
                carrito.limpiar()

        # Respuesta exitosa
        if is_json:
            return JsonResponse({
                'success': 'Compra procesada exitosamente',
                'orden_id': orden.id,
                'usuario': request.user.username,
                'fecha': orden.fecha.strftime("%Y-%m-%d %H:%M:%S"),  # Usando el campo correcto 'fecha'
                'total': total,
                'items': items_procesados
            }, status=201)
        else:
            return render(request, 'carrito/exito.html', {'mensaje': "Compra procesada exitosamente."})

    except Herramienta.DoesNotExist:
        error_msg = "Una de las herramientas no existe en la base de datos"
        if is_json:
            return JsonResponse({'error': error_msg}, status=404)
        else:
            messages.error(request, error_msg)
            return redirect("home")
    except Exception as e:
        error_msg = f"Ocurrió un error al procesar la compra: {str(e)}"
        if is_json:
            return JsonResponse({'error': error_msg}, status=500)
        else:
            messages.error(request, error_msg)
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
