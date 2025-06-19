from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
import json
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from herramientas.models import Herramienta, Categoria
from django.contrib.auth.models import User
from ordenes.models import ItemOrden, Orden
from django.views.decorators.csrf import csrf_exempt
from .forms import HerramientaForm
from autenticacion.decorators import bodeguero_required
from django.contrib import messages


@login_required
@bodeguero_required
def ver_usuarios_y_ordenes(request):
    is_json = request.content_type == 'application/json'
    
    # Obtener usuarios con órdenes
    usuarios = User.objects.all()
    
    # Preparar datos para respuesta JSON
    if is_json:
        usuarios_data = []
        
        for usuario in usuarios:
            # Obtener órdenes del usuario
            ordenes = Orden.objects.filter(usuario=usuario).order_by('-fecha')
            ordenes_data = []
            
            for orden in ordenes:
                # Obtener items de la orden
                items = ItemOrden.objects.filter(orden=orden)
                items_data = []
                
                for item in items:
                    items_data.append({
                        'herramienta_id': item.herramienta.id,
                        'nombre': item.herramienta.nombre,
                        'cantidad': item.cantidad,
                        'precio_unitario': float(item.precio),
                        'subtotal': float(item.cantidad * item.precio)
                    })
                
                ordenes_data.append({
                    'orden_id': orden.id,
                    'fecha': orden.fecha.strftime("%Y-%m-%d %H:%M:%S"),
                    'total_precio': float(orden.total_precio),
                    'cantidad_herramientas': orden.cantidad_herramientas,
                    'items': items_data
                })
            
            usuarios_data.append({
                'usuario_id': usuario.id,
                'username': usuario.username,
                'email': usuario.email,
                'ordenes': ordenes_data,
                'total_ordenes': len(ordenes)
            })
        
        # Obtener herramientas con formato
        herramientas = Herramienta.objects.all()
        herramientas_data = []
        
        for herramienta in herramientas:
            herramientas_data.append({
                'id': herramienta.id,
                'nombre': herramienta.nombre,
                'precio': float(herramienta.precio),
                'precio_clp': "{:,}".format(herramienta.precio),
                'cantidad': herramienta.cantidad,
            })
        
        return JsonResponse({
            'usuarios': usuarios_data,
            'herramientas': herramientas_data
        })
    
    else:
        # Comportamiento original para HTML
        usuarios = usuarios.prefetch_related('orden_set__items')
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
    
    # Verificar si es JSON (Postman)
    is_json = request.content_type == 'application/json'
    
    if is_json:
        # Construir respuesta JSON con los detalles de la herramienta
        return JsonResponse({
            'id': herramienta.id,
            'nombre': herramienta.nombre,
            'descripcion': herramienta.descripcion,
            'precio': float(herramienta.precio),
            'cantidad': herramienta.cantidad,
            'imagen': request.build_absolute_uri(herramienta.imagen.url) if herramienta.imagen else None,
        })
    else:
        # Comportamiento original para HTML
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
            return redirect('consultarstock')
    else:
        form = HerramientaForm()
    
    return render(request, 'bodeguero/agregarHerramienta.html', {'form': form})


## FUNCION EDITA DATOS DE HERRAMIENTA MEDIANTE METODO POST
@csrf_exempt
@login_required
@bodeguero_required
def editarHerramienta(request, herramienta_id):
    herramienta = get_object_or_404(Herramienta, pk=herramienta_id)
    is_json = request.content_type == 'application/json'
    if request.method == 'POST':
        if is_json:
            # Manejo para JSON (Postman)
            try:
                data = json.loads(request.body)
                
                # Actualizar campos
                herramienta.nombre = data.get('nombre', herramienta.nombre)
                herramienta.precio = data.get('precio', herramienta.precio)
                herramienta.descripcion = data.get('descripcion', herramienta.descripcion)
                herramienta.cantidad = data.get('cantidad', herramienta.cantidad)

                # Actualizar categoría si se proporciona
                categoria_id = data.get('categoria_id')
                if categoria_id:
                    try:
                        categoria = Categoria.objects.get(id=categoria_id)
                        herramienta.categoria = categoria
                    except Categoria.DoesNotExist:
                        pass
                
                herramienta.save()
                
                return JsonResponse({
                    'success': 'Herramienta actualizada correctamente',
                    'herramienta': {
                        'id': herramienta.id,
                        'nombre': herramienta.nombre,
                        'precio': float(herramienta.precio),
                        'descripcion': herramienta.descripcion,
                        'cantidad': herramienta.cantidad,
                        'imagen': request.build_absolute_uri(herramienta.imagen.url) if herramienta.imagen else None
                    }
                })
                
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Formato JSON inválido'}, status=400)
                
        else:
            # Manejo original para formularios web
            herramienta.nombre = request.POST.get('nombre')
            herramienta.precio = request.POST.get('precio')
            herramienta.descripcion = request.POST.get('descripcion')
            herramienta.cantidad = request.POST.get('cantidad')
            
            # Actualizar categoría
            categoria_id = request.POST.get('categoria')
            if categoria_id:
                categoria = Categoria.objects.get(id=categoria_id)
                herramienta.categoria = categoria

            if 'imagen' in request.FILES:
                herramienta.imagen = request.FILES['imagen']

            herramienta.save()
            return redirect('mostrar_stock', herramienta_id=herramienta.id)
    
    else:  # GET
        if is_json:
            # Devolver datos de la herramienta en JSON
            return JsonResponse({
                'id': herramienta.id,
                'nombre': herramienta.nombre,
                'precio': float(herramienta.precio),
                'descripcion': herramienta.descripcion,
                'cantidad': herramienta.cantidad,
                'categoria_id': herramienta.categoria.id if herramienta.categoria else None,
                'categoria_nombre': herramienta.categoria.nombre if herramienta.categoria else None,
                'imagen': request.build_absolute_uri(herramienta.imagen.url) if herramienta.imagen else None
            })
        else:
            # Renderizar formulario para web
            categorias = Categoria.objects.all()
            return render(request, 'bodeguero/editar_herramienta.html', {
                'herramienta': herramienta,
                'categorias': categorias
            })


@login_required
@bodeguero_required
@require_http_methods(["POST"])
def eliminarHerramienta(request, herramienta_id):
    herramienta = get_object_or_404(Herramienta, pk=herramienta_id)
    herramienta.delete()
    messages.success(request, f'Herramienta "{herramienta.nombre}" eliminada correctamente.')
    return redirect('bodeguero')


@login_required
@bodeguero_required
def ver_stock_general(request):
    herramientas = Herramienta.objects.all()

    for herramienta in herramientas:
        herramienta.precio_clp = "{:,}".format(herramienta.precio)

    return render(request, 'bodeguero/consultarstock.html', {'herramientas': herramientas})
