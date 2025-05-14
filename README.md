# Tienda de Comics - Proyecto Django

Este es un proyecto funcional en Django para "FerreMaX" 

--- --- --- --- ---

## Instalación

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/JhonnyBoy12/semestral-Integracion
   ```

2. Crear y activar un ambiente virtual:
   ```bash
   py -m venv myvenv
   .\myvenv\Scripts\Activate
   ```

3. Actualizar pip dentro del ambiente virtual:
   ```bash
   py -m pip install --upgrade pip
   ```

4. Instalar los requerimientos del proyecto desde `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

5. Ejecutar el servidor para iniciar la aplicación:
   ```bash
   python manage.py runserver
   ```

--- --- --- --- ---

### Funcionalidades del Proyecto

- **Carrito**: Los usuarios pueden agregar herramientas al carrito para comprar.
  
- **Herramientas**: Gestiona las herramientas disponibles para la venta. Los cambios se reflejan automáticamente en la interfaz web.
  
- **Inventario**: Vista de inventario para añadido stock y vistas de ordenes de usuarios.
  
- **Órdenes**: Gestiona las compras realizadas por los usuarios, quienes pueden ver el historial de sus compras en su interfaz de usuario.
  
- **TiendaWeb**: Gestiona archivos estáticos como CSS, JS, imágenes, etc., y proporciona bases extensibles para la interfaz de usuario.

- **Ferremas**: Proyecto carpeta principal donde instalamos apps y creamos urls.

--- --- ---

**Nota**: Asegúrate de configurar correctamente tu ambiente virtual antes de ejecutar el proyecto.

--- --- ---
