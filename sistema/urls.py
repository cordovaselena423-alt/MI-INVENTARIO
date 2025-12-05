from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Importamos TODAS las vistas (incluyendo la nueva generar_pdf)
from productos.views import (
    home, 
    agregar_producto, 
    editar_producto, 
    eliminar_producto, 
    registrar_entrada, 
    registrar_salida, 
    reportes, 
    configuracion,
    gestionar_contactos,
    generar_pdf  # <--- IMPORTANTE: Esta es la nueva función
)

urlpatterns = [
    # Panel de Administración
    path('admin/', admin.site.urls),
    
    # Sistema de Login
    path('accounts/', include('django.contrib.auth.urls')),
    
    # --- DASHBOARD ---
    path('', home, name='home'),
    
    # --- PRODUCTOS ---
    path('agregar/', agregar_producto, name='agregar'),
    path('editar/<int:id>/', editar_producto, name='editar'),
    path('eliminar/<int:id>/', eliminar_producto, name='eliminar'),
    
    # --- MOVIMIENTOS ---
    path('entrada/', registrar_entrada, name='entrada'),
    path('salida/', registrar_salida, name='salida'),
    
    # --- EXTRAS ---
    path('reportes/', reportes, name='reportes'),
    path('configuracion/', configuracion, name='configuracion'),
    path('contactos/', gestionar_contactos, name='contactos'),
    
    # --- RUTA PARA DESCARGAR PDF ---
    path('pdf/<int:id>/', generar_pdf, name='generar_pdf'),
]

# Configuración de Imágenes (Solo modo desarrollo)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)