from django.shortcuts import render

# Create your views here.
def home(request):
    context ={
        'mensaje': 'Hola Mundo'
    }
    return render(request, "herramientas/home.html",context)
