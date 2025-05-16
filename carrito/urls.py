from django.urls import path
from . import views

urlpatterns = [
    path('carrito', views.ver_carrito, name='carrito'),  
    path('agregar/<int:herramienta_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('aumentar/<int:herramienta_id>/', views.aumentar_cantidad, name='aumentar_cantidad'),
    path('disminuir/<int:herramienta_id>/', views.disminuir_cantidad, name='disminuir_cantidad'),
    path('eliminar/<int:herramienta_id>/', views.eliminar_producto, name='eliminar_producto'),
    path('vaciar/', views.vaciar_carrito, name='vaciar_carrito'),
]