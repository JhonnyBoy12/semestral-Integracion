from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.shortcuts import render, redirect


## FUNCION DE REGISTRO DE USURIOS CON "POST" WS
def registro_usuario(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        contra = request.POST.get('contra')
        contra2 = request.POST.get('contra2')

        if not all([username, email, contra, contra2]):
            return render(request, 'registro.html', {'error': 'Todos los campos son obligatorios.'})

        if contra != contra2:
            return render(request, 'registro.html', {'error': 'Las contraseñas no coinciden.'})

        if User.objects.filter(username=username).exists():
            return render(request, 'registro.html', {'error': 'El nombre de usuario ya existe.'})

        if User.objects.filter(email=email).exists():
            return render(request, 'registro.html', {'error': 'El correo ya está en uso.'})

        user = User.objects.create_user(username=username, email=email, password=contra)
        Token.objects.get_or_create(user=user)  # genera token

        return redirect('login')  # Cambia 'login' por el nombre correcto de tu URL de inicio de sesión

    return render(request, 'autenticacion/registro.html')

## FUNCION DE INICIO DE SESION CON "POST" WS
def iniciar_sesion(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  # Login clásico de Django
            token, created = Token.objects.get_or_create(user=user)  # genera o recupera token
            request.session['token'] = token.key  # lo puedes guardar en la sesión si quieres usarlo
            return redirect('home')  # redirige a la página principal
        else:
            return render(request, 'autenticacion/login.html', {'error': 'Credenciales inválidas.'})

    return render(request, 'autenticacion/inicioSesion.html')

from django.contrib.auth import logout

##FUNCION PARA CERRAR SESION Y ELIMINAR TOKEN NO QUEDE REGISTRADO
def cerrar_sesion(request):
    if request.user.is_authenticated:
        Token.objects.filter(user=request.user).delete()  # eliminar el token si existe
        logout(request)  # cerrar sesión
    return redirect('login')  # redirigir al login
