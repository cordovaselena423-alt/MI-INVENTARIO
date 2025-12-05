from django import forms
from .models import Producto, Perfil, Cliente, Proveedor

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'precio', 'stock_minimo', 'imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
        }

# --- FORMULARIOS PARA CREAR CONTACTOS ---
class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'dni_ruc', 'telefono']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre o Razón Social'}),
            'dni_ruc': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'DNI o RUC'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
        }

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'ruc', 'telefono']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre Empresa'}),
            'ruc': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'RUC'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
        }

# --- ENTRADA (CON PROVEEDOR) ---
class EntradaForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super(EntradaForm, self).__init__(*args, **kwargs)
        self.fields['producto'].queryset = Producto.objects.filter(usuario=user)
        self.fields['proveedor'].queryset = Proveedor.objects.filter(usuario=user) # Solo mis proveedores

    producto = forms.ModelChoiceField(queryset=Producto.objects.none(), widget=forms.Select(attrs={'class': 'form-select'}))
    proveedor = forms.ModelChoiceField(queryset=Proveedor.objects.none(), required=False, empty_label="-- Sin Proveedor --", widget=forms.Select(attrs={'class': 'form-select'}))
    cantidad = forms.IntegerField(min_value=1, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    numero_lote = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    fecha_vencimiento = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))

# --- SALIDA (CON CLIENTE) ---
class SalidaForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super(SalidaForm, self).__init__(*args, **kwargs)
        self.fields['producto'].queryset = Producto.objects.filter(usuario=user)
        self.fields['cliente'].queryset = Cliente.objects.filter(usuario=user) # Solo mis clientes

    producto = forms.ModelChoiceField(queryset=Producto.objects.none(), widget=forms.Select(attrs={'class': 'form-select'}))
    cliente = forms.ModelChoiceField(queryset=Cliente.objects.none(), required=False, empty_label="-- Sin Cliente --", widget=forms.Select(attrs={'class': 'form-select'}))
    cantidad = forms.IntegerField(min_value=1, widget=forms.NumberInput(attrs={'class': 'form-control'}))

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['logo']
        widgets = {'logo': forms.FileInput(attrs={'class': 'form-control'})}