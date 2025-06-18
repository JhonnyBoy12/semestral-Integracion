from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from inventario.models import Profile
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json

from inventario.models import Profile  

@csrf_exempt
def registro_usuario(request):
    # Verificar si es JSON
    is_json = request.content_type == 'application/json'
    
    if request.method == 'POST':
        # Obtener datos según el tipo de contenido
        if is_json:
            try:
                data = json.loads(request.body)
                username = data.get('username')
                email = data.get('email')
                contra = data.get('contra')
                contra2 = data.get('contra2')
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Formato JSON inválido'}, status=400)
        else:
            username = request.POST.get('username')
            email = request.POST.get('email')
            contra = request.POST.get('contra')
            contra2 = request.POST.get('contra2')

        # Validaciones (mantenemos las existentes)
        if not all([username, email, contra, contra2]):
            error = 'Todos los campos son obligatorios.'
            return JsonResponse({'error': error}, status=400) if is_json else render(request, 'autenticacion/registro.html', {'error': error})

        if contra != contra2:
            error = 'Las contraseñas no coinciden.'
            return JsonResponse({'error': error}, status=400) if is_json else render(request, 'autenticacion/registro.html', {'error': error})

        if User.objects.filter(username=username).exists():
            error = 'El nombre de usuario ya existe.'
            return JsonResponse({'error': error}, status=400) if is_json else render(request, 'autenticacion/registro.html', {'error': error})

        if User.objects.filter(email=email).exists():
            error = 'El correo ya está en uso.'
            return JsonResponse({'error': error}, status=400) if is_json else render(request, 'autenticacion/registro.html', {'error': error})

        # Crear usuario
        user = User.objects.create_user(username=username, email=email, password=contra)
        
        # Respuesta según el tipo de contenido
        if is_json:
            # Generar token si es necesario (opcional)
            token, _ = Token.objects.get_or_create(user=user)
            return JsonResponse({
                'success': 'Usuario registrado',
                'user_id': user.id,
                'token': token.key  # Solo si estás usando DRF Tokens
            }, status=201)
        else:
            return redirect('login')

    # GET request
    return JsonResponse({'error': 'Método no permitido'}, status=405) if is_json else render(request, 'autenticacion/registro.html')

## FUNCION DE INICIO DE SESION CON "POST" WS
@csrf_exempt
def iniciar_sesion(request):
    # Verificar si es JSON
    is_json = request.content_type == 'application/json'
    
    if request.method == 'POST':
        # Obtener datos según el tipo de contenido
        if is_json:
            try:
                data = json.loads(request.body)
                username = data.get('username')
                password = data.get('password')
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Formato JSON inválido'}, status=400)
        else:
            username = request.POST.get('username')
            password = request.POST.get('password')
        
        # Validación básica
        if not username or not password:
            error = 'Se requieren nombre de usuario y contraseña.'
            if is_json:
                return JsonResponse({'error': error}, status=400)
            else:
                return render(request, 'autenticacion/inicioSesion.html', {'error': error})
        
        # Verificar existencia del usuario
        if not User.objects.filter(username=username).exists():
            error = 'El usuario no existe.'
            if is_json:
                return JsonResponse({'error': error}, status=400)
            else:
                return render(request, 'autenticacion/inicioSesion.html', {'error': error})
        
        # Autenticar
        user = authenticate(request, username=username, password=password)
        if user is None:
            error = 'La contraseña es incorrecta.'
            if is_json:
                return JsonResponse({'error': error}, status=400)
            else:
                return render(request, 'autenticacion/inicioSesion.html', {'error': error})
        
        # Iniciar sesión
        login(request, user)
        
        # Obtener o crear token
        token, created = Token.objects.get_or_create(user=user)
        
        # Obtener perfil
        try:
            perfil = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            perfil = None
        
        # Para solicitudes JSON, devolver datos relevantes
        if is_json:
            response_data = {
                'success': 'Inicio de sesión exitoso',
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'token': token.key,
                'rol': perfil.rol if perfil else None
            }
            return JsonResponse(response_data)
        else:
            # Para HTML, establecer la sesión y redirigir
            request.session['token'] = token.key
            if perfil:
                if perfil.rol in ['bodeguero', 'admin']:
                    request.session['staff_access'] = True
                
                # Redirección según rol
                if perfil.rol == 'bodeguero':
                    return redirect('bodeguero')
                elif perfil.rol == 'admin':
                    return redirect('bodeguero')  # Cambia esto si tienes otra vista para admin
            return redirect('home')
    
    # Si es GET, mostrar el formulario
    return render(request, 'autenticacion/inicioSesion.html')

from django.contrib.auth import logout

##FUNCION PARA CERRAR SESION Y ELIMINAR TOKEN NO QUEDE REGISTRADO
@csrf_exempt
@login_required
def cerrar_sesion(request):
    # Verificar si es JSON
    is_json = request.content_type == 'application/json'
    
    try:
        # 1. Eliminar el token de autenticación (si existe)
        if request.user.is_authenticated:
            Token.objects.filter(user=request.user).delete()
        
        # 2. Limpiar variables de sesión
        session_keys_to_delete = ['token', 'bodeguero_access', 'staff_access']
        for key in session_keys_to_delete:
            if key in request.session:
                del request.session[key]
        
        # 3. Cerrar sesión y limpiar
        logout(request)
        request.session.flush()
        
        # 4. Respuesta según el tipo de contenido
        if is_json:
            return JsonResponse({'success': 'Sesión cerrada correctamente'})
        else:
            return redirect('login')
    
    except Exception as e:
        # Si ocurre algún error, igualmente cerramos sesión
        logout(request)
        request.session.flush()
        if is_json:
            return JsonResponse({'error': str(e)}, status=500)
        else:
            return redirect('login')
