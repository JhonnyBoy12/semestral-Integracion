from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from inventario.models import Profile
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from inventario.models import Profile  # Asegúrate de tener este import

def registro_usuario(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        contra = request.POST.get('contra')
        contra2 = request.POST.get('contra2')

        if not all([username, email, contra, contra2]):
            return render(request, 'autenticacion/registro.html', {'error': 'Todos los campos son obligatorios.'})

        if contra != contra2:
            return render(request, 'autenticacion/registro.html', {'error': 'Las contraseñas no coinciden.'})

        if User.objects.filter(username=username).exists():
            return render(request, 'autenticacion/registro.html', {'error': 'El nombre de usuario ya existe.'})

        if User.objects.filter(email=email).exists():
            return render(request, 'autenticacion/registro.html', {'error': 'El correo ya está en uso.'})

        # Solo creas el usuario, lo demás lo hace la señal
        user = User.objects.create_user(username=username, email=email, password=contra)
        return redirect('login')

    return render(request, 'autenticacion/registro.html')

## FUNCION DE INICIO DE SESION CON "POST" WS
def iniciar_sesion(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not User.objects.filter(username=username).exists():
            error = 'El usuario no existe.'
        else:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                token, created = Token.objects.get_or_create(user=user)
                request.session['token'] = token.key

                perfil = Profile.objects.get(user=user)
                
                # Establecer flags de sesión según el rol
                if perfil.rol in ['bodeguero', 'admin']:
                    request.session['staff_access'] = True
                
                # Redirección según rol
                if perfil.rol == 'bodeguero':
                    return redirect('bodeguero')
                elif perfil.rol == 'admin':
                    return redirect('bodeguero')  # O podrías redirigir a un dashboard específico
                else:
                    return redirect('home')
            else:
                error = 'La contraseña es incorrecta.'

        return render(request, 'autenticacion/inicioSesion.html', {'error': error})

    return render(request, 'autenticacion/inicioSesion.html')

from django.contrib.auth import logout

##FUNCION PARA CERRAR SESION Y ELIMINAR TOKEN NO QUEDE REGISTRADO
@login_required  # Asegura que solo usuarios autenticados puedan cerrar sesión
def cerrar_sesion(request):
    try:
        # 1. Eliminar el token de autenticación (si existe)
        if request.user.is_authenticated:
            Token.objects.filter(user=request.user).delete()
        
        # 2. Limpiar variables de sesión
        session_keys_to_delete = ['token', 'bodeguero_access']
        for key in session_keys_to_delete:
            if key in request.session:
                del request.session[key]
        
        # 3. Cerrar sesión y limpiar
        logout(request)
        request.session.flush()
        
        # 4. Redirigir al login
        return redirect('login')
    
    except Exception as e:
        # Si ocurre algún error, igualmente cerramos sesión
        logout(request)
        request.session.flush()
        return redirect('login')
