from django.urls import path
from . import views

urlpatterns = [
    path('misPedidos/', views.mis_pedidos, name='misPedidos'),
    #path('procesar_compra/', views.procesar_compra, name='procesar_compra'),
    
]