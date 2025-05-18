from django.http import HttpResponseForbidden
from functools import wraps

def bodeguero_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden("Acceso no autorizado - Debes iniciar sesión")
        
        # Verifica si el usuario tiene perfil y es bodeguero
        if not hasattr(request.user, 'profile'):
            return HttpResponseForbidden("Acceso no autorizado - Perfil no encontrado")
            
        if request.user.profile.rol != 'bodeguero':
            return HttpResponseForbidden("Acceso no autorizado - No tienes permisos de bodeguero")
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view