class Carrito:
    def __init__(self, request):
        self.request = request
        self.session = request.session
        self.carro = self.session.get('carrito', {})

    def limpiar(self):
        self.session['carrito'] = {}
        self.session.modified = True