from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, F
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.utils import timezone
from datetime import timedelta

# --- IMPORTACIONES PARA PDF (NUEVO) ---
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

# --- TUS MODELOS Y FORMULARIOS ---
from .models import Producto, Lote, Movimiento, Perfil, Cliente, Proveedor
from .forms import ProductoForm, EntradaForm, SalidaForm, PerfilForm, ClienteForm, ProveedorForm

# --- VISTA PRINCIPAL (DASHBOARD) ---
@login_required
def home(request):
    try:
        mi_perfil = request.user.perfil
        logo_empresa = mi_perfil.logo
    except:
        logo_empresa = None

    busqueda = request.GET.get('buscar')
    
    if busqueda:
        mis_productos = Producto.objects.filter(usuario=request.user, nombre__icontains=busqueda).order_by('nombre')
    else:
        mis_productos = Producto.objects.filter(usuario=request.user).order_by('nombre')

    # Cálculos
    total_raw = 0
    for p in mis_productos:
        total_raw += p.precio * p.stock_total
    total_dinero = "{:,.2f}".format(total_raw)

    alertas = [p for p in mis_productos if p.stock_total <= p.stock_minimo]
    total_criticos = len(alertas)

    fecha_limite = timezone.now().date() + timedelta(days=30)
    lotes_vencimiento = Lote.objects.filter(
        producto__usuario=request.user,
        cantidad__gt=0,
        fecha_vencimiento__range=[timezone.now().date(), fecha_limite]
    ).count()

    return render(request, 'home.html', {
        'productos': mis_productos,
        'alertas': alertas,
        'total_dinero': total_dinero,
        'total_criticos': total_criticos,
        'lotes_vencimiento': lotes_vencimiento,
        'logo_empresa': logo_empresa,
    })

# --- GESTIÓN DE CONTACTOS (CLIENTES/PROVEEDORES) ---
@login_required
def gestionar_contactos(request):
    if request.method == 'POST':
        if 'crear_cliente' in request.POST:
            form = ClienteForm(request.POST)
            if form.is_valid():
                cliente = form.save(commit=False)
                cliente.usuario = request.user
                cliente.save()
                messages.success(request, 'Cliente agregado.')
        elif 'crear_proveedor' in request.POST:
            form = ProveedorForm(request.POST)
            if form.is_valid():
                proveedor = form.save(commit=False)
                proveedor.usuario = request.user
                proveedor.save()
                messages.success(request, 'Proveedor agregado.')
        return redirect('contactos')
    
    mis_clientes = Cliente.objects.filter(usuario=request.user)
    mis_proveedores = Proveedor.objects.filter(usuario=request.user)
    
    return render(request, 'contactos.html', {
        'cliente_form': ClienteForm(),
        'proveedor_form': ProveedorForm(),
        'clientes': mis_clientes,
        'proveedores': mis_proveedores
    })

# --- GESTIÓN DE PRODUCTOS ---
@login_required
def agregar_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save(commit=False)
            producto.usuario = request.user
            producto.save()
            messages.success(request, 'Producto creado.')
            return redirect('home')
    else:
        form = ProductoForm()
    return render(request, 'agregar.html', {'form': form, 'titulo': 'Nuevo Producto'})

@login_required
def editar_producto(request, id):
    producto = get_object_or_404(Producto, id=id, usuario=request.user)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Actualizado.')
            return redirect('home')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'agregar.html', {'form': form, 'titulo': 'Editar Producto'})

@login_required
def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, id=id, usuario=request.user)
    producto.delete()
    messages.warning(request, 'Eliminado.')
    return redirect('home')

# --- MOVIMIENTOS (ENTRADA/SALIDA) ---
@login_required
def registrar_entrada(request):
    if request.method == 'POST':
        form = EntradaForm(request.user, request.POST)
        if form.is_valid():
            prod = form.cleaned_data['producto']
            prov = form.cleaned_data['proveedor']
            cant = form.cleaned_data['cantidad']
            lote_num = form.cleaned_data['numero_lote']
            vence = form.cleaned_data['fecha_vencimiento']

            lote_obj, created = Lote.objects.get_or_create(
                producto=prod, numero_lote=lote_num,
                defaults={'fecha_vencimiento': vence}
            )
            lote_obj.cantidad += cant
            lote_obj.save()

            Movimiento.objects.create(producto=prod, tipo='ENTRADA', cantidad=cant, detalle=f"Lote {lote_num}", proveedor=prov)
            messages.success(request, 'Entrada registrada.')
            return redirect('home')
    else:
        form = EntradaForm(request.user)
    return render(request, 'agregar.html', {'form': form, 'titulo': 'Registrar Entrada'})

@login_required
def registrar_salida(request):
    if request.method == 'POST':
        form = SalidaForm(request.user, request.POST)
        if form.is_valid():
            prod = form.cleaned_data['producto']
            clie = form.cleaned_data['cliente']
            cant_retirar = form.cleaned_data['cantidad']

            if prod.stock_total < cant_retirar:
                messages.error(request, f"Stock insuficiente. Tienes {prod.stock_total}.")
            else:
                lotes = prod.lotes.filter(cantidad__gt=0).order_by('fecha_vencimiento')
                pendiente = cant_retirar
                detalle_txt = []
                for lote in lotes:
                    if pendiente <= 0: break
                    tomar = min(pendiente, lote.cantidad)
                    lote.cantidad -= tomar
                    detalle_txt.append(f"{tomar} ({lote.numero_lote})")
                    pendiente -= tomar
                    lote.save()

                Movimiento.objects.create(producto=prod, tipo='SALIDA', cantidad=cant_retirar, detalle=", ".join(detalle_txt), cliente=clie)
                messages.success(request, 'Salida registrada.')
                return redirect('home')
    else:
        form = SalidaForm(request.user)
    return render(request, 'agregar.html', {'form': form, 'titulo': 'Registrar Salida'})

# --- REPORTES Y CONFIGURACIÓN ---
@login_required
def reportes(request):
    movimientos = Movimiento.objects.filter(producto__usuario=request.user).order_by('-fecha')
    if request.GET.get('fecha_inicio') and request.GET.get('fecha_fin'):
        movimientos = movimientos.filter(fecha__range=[request.GET.get('fecha_inicio'), request.GET.get('fecha_fin')])

    return render(request, 'reportes.html', {
        'movimientos': movimientos,
        'total_entradas': movimientos.filter(tipo='ENTRADA').count(),
        'total_salidas': movimientos.filter(tipo='SALIDA').count()
    })

@login_required
def configuracion(request):
    perfil, created = Perfil.objects.get_or_create(usuario=request.user)

    if request.method == 'POST':
        if 'guardar_logo' in request.POST:
            logo_form = PerfilForm(request.POST, request.FILES, instance=perfil)
            if logo_form.is_valid():
                logo_form.save()
                messages.success(request, 'Logo de empresa actualizado.')
                return redirect('home')
        
        elif 'guardar_pass' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Contraseña actualizada.')
                return redirect('home')

    logo_form = PerfilForm(instance=perfil)
    password_form = PasswordChangeForm(request.user)

    return render(request, 'configuracion.html', {
        'logo_form': logo_form,
        'password_form': password_form
    })

# --- NUEVA FUNCIÓN: GENERAR PDF ---
@login_required
def generar_pdf(request, id):
    # 1. Buscamos datos
    movimiento = get_object_or_404(Movimiento, id=id, producto__usuario=request.user)
    try:
        perfil = request.user.perfil
    except:
        perfil = None

    # 2. TRUCO PARA EL LOGO: Obtener ruta absoluta del disco
    logo_path = None
    if perfil and perfil.logo:
        # Esto nos da algo tipo: C:\Users\TuUsuario\Proyecto\media\logos\imagen.jpg
        logo_path = perfil.logo.path 

    # 3. Título
    titulo = "NOTA DE ENTRADA" if movimiento.tipo == 'ENTRADA' else "NOTA DE SALIDA"

    # 4. Contexto
    context = {
        'movimiento': movimiento,
        'perfil': perfil,
        'logo_path': logo_path,  # <--- ENVIAMOS LA RUTA EXACTA
        'titulo': titulo,
        'fecha_hoy': timezone.now().date(),
        'request': request, 
    }

    # 5. Renderizar
    template_path = 'pdf_template.html'
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Nota_{movimiento.id}.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    # Crear PDF
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error al generar PDF <pre>' + html + '</pre>')
    return response