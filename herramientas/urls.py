from django.urls import path

from . import views

urlpatterns = [    
    path('home/', views.home, name= "home"),
    path('herramientas/<int:herramienta_id>/', views.herramienta_detalles, name="herramienta_detalles"),
]