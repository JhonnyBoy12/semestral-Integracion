from django.urls import path
from . import views

urlpatterns = [
    path('misPedidos/', views.mis_pedidos, name='misPedidos'),
]