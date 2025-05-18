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
        ]
        
        if request.path in public_urls:
            return None
            
        # Verificación para rutas de inventario
        if request.path.startswith('/inventario/'):
            # Verificar autenticación primero
            if not request.user.is_authenticated:
                return redirect('login')
                
            # Verificar si es bodeguero
            try:
                if not hasattr(request.user, 'profile') or request.user.profile.rol != 'bodeguero':
                    return HttpResponseForbidden("No tienes permisos de bodeguero")
            except Exception:
                return HttpResponseForbidden("Error verificando perfil")
            
            # Permitir acceso si viene de otra vista de inventario
            if request.META.get('HTTP_REFERER', '').startswith(request.build_absolute_uri('/inventario/')):
                return None
                
            # Permitir acceso si tiene el flag de sesión
            if request.session.get('bodeguero_access', False):
                return None
                
            return HttpResponseForbidden("Acceso no autorizado")
        
        return None