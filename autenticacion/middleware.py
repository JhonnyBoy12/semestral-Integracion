from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse

class BodegueroAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # URLs públicas excluidas
        public_urls = [
            reverse('login'),
            reverse('logout'),
            reverse('home'),
            reverse('registro'),
            # Añade aquí otras URLs públicas si es necesario
        ]
        
        # Permitir acceso a URLs públicas
        if request.path in public_urls:
            return None
            
        # Verificación para rutas de inventario
        if request.path.startswith('/inventario/'):
            # Verificar autenticación primero
            if not request.user.is_authenticated:
                return redirect('login')
                
            # Verificar si el usuario tiene perfil
            if not hasattr(request.user, 'profile'):
                return HttpResponseForbidden("Perfil de usuario no encontrado")
                
            # Verificar roles permitidos (bodeguero o admin)
            if request.user.profile.rol not in ['bodeguero', 'admin']:
                return HttpResponseForbidden("No tienes permisos para acceder a esta sección")
                
            # Si pasa todas las verificaciones, permitir acceso
            return None
        return None