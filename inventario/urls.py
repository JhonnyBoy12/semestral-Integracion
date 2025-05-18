from django.urls import path
from django.contrib.auth.decorators import login_required
from autenticacion.decorators import bodeguero_required
from . import views

# Aplicamos los decoradores a todas las vistas
urlpatterns = [  
    path('stock/<int:herramienta_id>/', views.consultarStock, name='mostrar_stock'),
    path('aumentar-stock/<int:herramienta_id>/', views.aumentarStock, name='aumentar_stock'),
    path('agregar-herramienta', views.agregarHerramienta, name='agregar_herramienta'),
    path('editar_herramienta/<int:herramienta_id>/', views.editarHerramienta, name='editar_herramienta'),
    path('bodeguero/', views.ver_usuarios_y_ordenes, name='bodeguero'),
]