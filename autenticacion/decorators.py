from django.http import HttpResponseForbidden
from functools import wraps

def bodeguero_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden("Acceso no autorizado - Debes iniciar sesión")
        
        # Verifica si el usuario tiene perfil
        if not hasattr(request.user, 'profile'):
            return HttpResponseForbidden("Acceso no autorizado - Perfil no encontrado")
            
        # Verifica si tiene rol de staff (bodeguero o admin)
        if request.user.profile.rol not in ['bodeguero', 'admin']:
            return HttpResponseForbidden("Acceso no autorizado - No tienes permisos suficientes")
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view