from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile

# Muestra el perfil embebido dentro del usuario
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Perfil'
    fk_name = 'user'  # Asegura que use la relación correcta

class CustomUserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)

    # Opcional: mostrar el rol en la lista de usuarios
    def rol(self, obj):
        return obj.profile.rol if hasattr(obj, 'profile') else 'Sin perfil'
    rol.short_description = 'Rol'
    list_display = BaseUserAdmin.list_display + ('rol',)

# Reemplaza el admin por defecto del modelo User
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)