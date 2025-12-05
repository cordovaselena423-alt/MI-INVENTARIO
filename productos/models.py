from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User

# --- PERFIL DE EMPRESA (LOGO) ---
class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    def __str__(self): return f"Perfil de {self.usuario.username}"

# --- NUEVOS MODELOS: CLIENTES Y PROVEEDORES ---
class Proveedor(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    ruc = models.CharField(max_length=20, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self): return self.nombre

class Cliente(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    dni_ruc = models.CharField(max_length=20, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self): return self.nombre

# --- TUS MODELOS DE SIEMPRE ---
class Producto(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    stock_minimo = models.IntegerField(default=5)

    def __str__(self): return self.nombre

    @property
    def stock_total(self):
        total = self.lotes.aggregate(total=Sum('cantidad'))['total']
        return total if total else 0

class Lote(models.Model):
    producto = models.ForeignKey(Producto, related_name='lotes', on_delete=models.CASCADE)
    numero_lote = models.CharField(max_length=50)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    cantidad = models.PositiveIntegerField(default=0)

class Movimiento(models.Model):
    TIPOS = [('ENTRADA', 'Entrada'), ('SALIDA', 'Salida')]
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10, choices=TIPOS)
    cantidad = models.PositiveIntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    detalle = models.CharField(max_length=200, blank=True)
    
    # NUEVOS CAMPOS (OPCIONALES)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)