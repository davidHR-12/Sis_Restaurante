from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test
from .models import Cliente, Menu, OrderDetail, Order, SystemConfig
from .forms import ClienteForm, BuscarClienteForm, MenuForm, BuscarMenuForm, OrderForm, OrderDetailForm, BuscarOrderForm, SystemConfigForm

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.db.models import Sum, Count, Q
from datetime import datetime, timedelta
from decimal import Decimal

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, LongTable, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

# Funciones para el login


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)

                return redirect('home')
            else:
                messages.error(
                    request, 'El usuario o contraseña es incorrecto')
        else:
            messages.error(request, 'Por favor, complete todos los campos')
    return render(request, 'login.html')


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def home(request):
    # Últimos pedidos (últimos 5)
    ultimos_pedidos = Order.objects.select_related(
        'cliente').order_by('-fecha_registro')[:3]

    # Calcular total de cada pedido
    for pedido in ultimos_pedidos:
        pedido.total_precio = sum(
            float(detail.menu.precio) * detail.cantidad
            for detail in pedido.orderdetail_set.all()
        )

    context = {
        'ultimos_pedidos': ultimos_pedidos,
    }
    return render(request, 'home.html', context)

# ---------------------------------------------------------------------
# LISTAR CLIENTES
# ---------------------------------------------------------------------


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def cliente_list(request):
    clientes = Cliente.objects.all().order_by("id")
    form = ClienteForm()
    return render(request, "client.html", {
        "clientes": clientes,
        "form": form,
    })


def is_superuser(user):
    return user.is_superuser
# ---------------------------------------------------------------------
# CONFIGURACIÓN DEL SISTEMA (Solo Administradores)
# ---------------------------------------------------------------------


@login_required
@user_passes_test(is_superuser)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_settings(request):
    """
    Vista para que el administrador configure el sistema
    """
    config = SystemConfig.get_config()

    if request.method == 'POST':
        form = SystemConfigForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Configuración actualizada correctamente')
            return redirect('admin_settings')
    else:
        form = SystemConfigForm(instance=config)

    return render(request, 'admin_settings.html', {
        'form': form,
        'config': config
    })


# ---------------------------------------------------------------------
# PANEL DE ADMINISTRACIÓN PRINCIPAL
# ---------------------------------------------------------------------
@login_required
@user_passes_test(is_superuser)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_panel(request):
    """
    Panel principal de administración con dashboard y pestañas
    """
    config = SystemConfig.get_config()

    # ========== ESTADÍSTICAS PARA DASHBOARD ==========
    # Total de clientes
    total_clientes = Cliente.objects.count()

    # Total de pedidos
    total_pedidos = Order.objects.count()

    # Pedidos de hoy
    hoy = datetime.now().date()
    pedidos_hoy = Order.objects.filter(fecha_registro__date=hoy).count()

    # Pedidos por estado
    pedidos_por_estado = Order.objects.values('estado').annotate(
        total=Count('id')
    ).order_by('estado')

    # Calcular ingresos totales
    orders_con_detalles = Order.objects.filter(estado='Entregado').prefetch_related(
        'orderdetail_set__menu').all()
    ingresos_totales = Decimal('0.00')
    ingresos_hoy = Decimal('0.00')

    for order in orders_con_detalles:
        subtotal = sum(
            float(detail.menu.precio) * detail.cantidad
            for detail in order.orderdetail_set.all()
        )
        itbis = subtotal * (float(config.itbis_rate) / 100)
        total_con_itbis = Decimal(str(subtotal + itbis))
        ingresos_totales += total_con_itbis

        # Ingresos de hoy
        if order.fecha_registro.date() == hoy:
            ingresos_hoy += total_con_itbis

    # Platillos más vendidos (top 5)
    platillos_vendidos = OrderDetail.objects.filter(
        order__estado='Entregado'  # o el estado que consideres
    ).values(
        'menu__nombre'
    ).annotate(
        total_cantidad=Sum('cantidad')
    ).order_by('-total_cantidad')[:5]

    # Últimos pedidos (últimos 5)
    ultimos_pedidos = Order.objects.select_related(
        'cliente').order_by('-fecha_registro')[:5]

    # Calcular total de cada pedido
    for pedido in ultimos_pedidos:
        pedido.total_precio = sum(
            float(detail.menu.precio) * detail.cantidad
            for detail in pedido.orderdetail_set.all()
        )

    # ========== GESTIÓN DE USUARIOS ==========
    usuarios = User.objects.all().order_by('-date_joined')

    # ========== INFORMACIÓN DEL USUARIO ACTUAL ==========
    current_user = request.user

    context = {
        'config': config,
        # Dashboard stats
        'total_clientes': total_clientes,
        'total_pedidos': total_pedidos,
        'pedidos_hoy': pedidos_hoy,
        'pedidos_por_estado': pedidos_por_estado,
        'ingresos_totales': ingresos_totales,
        'ingresos_hoy': ingresos_hoy,
        'platillos_vendidos': platillos_vendidos,
        'ultimos_pedidos': ultimos_pedidos,
        # Users
        'usuarios': usuarios,
        'current_user': current_user,
    }

    return render(request, 'admin_panel.html', context)


# ---------------------------------------------------------------------
# ACTUALIZAR CONFIGURACIÓN DEL SISTEMA
# ---------------------------------------------------------------------
@login_required
@user_passes_test(is_superuser)
def admin_update_config(request):
    """
    Actualizar configuración del sistema
    """
    config = SystemConfig.get_config()

    if request.method == 'POST':
        form = SystemConfigForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Configuración actualizada correctamente')
        else:
            messages.error(request, 'Error al actualizar la configuración')

    return redirect('admin_panel')


# ---------------------------------------------------------------------
# CREAR USUARIO
# ---------------------------------------------------------------------
@login_required
@user_passes_test(is_superuser)
def admin_create_user(request):
    """
    Crear nuevo usuario
    """
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        is_staff = request.POST.get('is_staff') == 'on'
        is_superuser = request.POST.get('is_superuser') == 'on'

        # Validaciones
        if not username or not password:
            messages.error(
                request, 'El nombre de usuario y la contraseña son obligatorios')
            return redirect('admin_panel')

        if password != password_confirm:
            messages.error(request, 'Las contraseñas no coinciden')
            return redirect('admin_panel')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya existe')
            return redirect('admin_panel')

        # Crear usuario
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            user.is_staff = is_staff
            user.is_superuser = is_superuser
            user.save()

            messages.success(
                request, f'Usuario {username} creado correctamente')
        except Exception as e:
            messages.error(request, f'Error al crear usuario: {str(e)}')

    return redirect('admin_panel')


# ---------------------------------------------------------------------
# ACTUALIZAR USUARIO
# ---------------------------------------------------------------------
@login_required
@user_passes_test(is_superuser)
def admin_update_user(request):
    """
    Actualizar información de usuario
    """
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = get_object_or_404(User, pk=user_id)

        # No permitir que el usuario se quite sus propios permisos de superusuario
        if user.id == request.user.id and request.POST.get('is_superuser') != 'on':
            messages.error(
                request, 'No puedes quitarte tus propios permisos de superusuario')
            return redirect('admin_panel')

        user.username = request.POST.get('username', user.username).strip()
        user.email = request.POST.get('email', user.email).strip()
        user.is_staff = request.POST.get('is_staff') == 'on'
        user.is_superuser = request.POST.get('is_superuser') == 'on'
        user.is_active = request.POST.get('is_active') == 'on'

        # Cambiar contraseña si se proporciona
        new_password = request.POST.get('new_password', '').strip()
        if new_password:
            user.set_password(new_password)

        try:
            user.save()
            messages.success(
                request, f'Usuario {user.username} actualizado correctamente')
        except Exception as e:
            messages.error(request, f'Error al actualizar usuario: {str(e)}')

    return redirect('admin_panel')


# ---------------------------------------------------------------------
# ELIMINAR USUARIO
# ---------------------------------------------------------------------
@login_required
@user_passes_test(is_superuser)
def admin_delete_user(request):
    """
    Eliminar usuario
    """
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = get_object_or_404(User, pk=user_id)

        # No permitir que el usuario se elimine a sí mismo
        if user.id == request.user.id:
            messages.error(request, 'No puedes eliminarte a ti mismo')
            return redirect('admin_panel')

        username = user.username
        user.delete()
        messages.success(
            request, f'Usuario {username} eliminado correctamente')

    return redirect('admin_panel')


# ---------------------------------------------------------------------
# ACTUALIZAR PERFIL DEL ADMINISTRADOR
# ---------------------------------------------------------------------
@login_required
@user_passes_test(is_superuser)
def admin_update_profile(request):
    """
    Actualizar perfil del administrador actual
    """
    if request.method == 'POST':
        user = request.user
        user.username = request.POST.get('username', user.username).strip()
        user.email = request.POST.get('email', user.email).strip()
        user.first_name = request.POST.get(
            'first_name', user.first_name).strip()
        user.last_name = request.POST.get('last_name', user.last_name).strip()

        try:
            user.save()
            messages.success(request, 'Perfil actualizado correctamente')
        except Exception as e:
            messages.error(request, f'Error al actualizar perfil: {str(e)}')

    return redirect('admin_panel')


# ---------------------------------------------------------------------
# CAMBIAR CONTRASEÑA DEL ADMINISTRADOR
# ---------------------------------------------------------------------
@login_required
@user_passes_test(is_superuser)
def admin_change_password(request):
    """
    Cambiar contraseña del administrador actual
    """
    if request.method == 'POST':
        current_password = request.POST.get('current_password', '')
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')

        # Verificar contraseña actual
        if not request.user.check_password(current_password):
            messages.error(request, 'La contraseña actual es incorrecta')
            return redirect('admin_panel')

        # Verificar que las contraseñas nuevas coincidan
        if new_password != confirm_password:
            messages.error(request, 'Las contraseñas nuevas no coinciden')
            return redirect('admin_panel')

        # Verificar longitud mínima
        if len(new_password) < 8:
            messages.error(
                request, 'La contraseña debe tener al menos 8 caracteres')
            return redirect('admin_panel')

        # Cambiar contraseña
        request.user.set_password(new_password)
        request.user.save()

        # Mantener la sesión activa después del cambio
        update_session_auth_hash(request, request.user)

        messages.success(request, 'Contraseña actualizada correctamente')

    return redirect('admin_panel')


# ---------------------------------------------------------------------
# BUSCAR CLIENTES
# ---------------------------------------------------------------------
@login_required
def cliente_buscar(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre", "")
        clientes = Cliente.objects.filter(nombre__icontains=nombre)
    else:
        return redirect("clientes")

    form = ClienteForm()
    return render(request, "client.html", {
        "clientes": clientes,
        "form": form,
    })


# ---------------------------------------------------------------------
# AGREGAR CLIENTE
# ---------------------------------------------------------------------
@login_required
def cliente_agregar(request):
    if request.method == "POST":
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
    return redirect("clientes")


# ---------------------------------------------------------------------
# ACTUALIZAR CLIENTE
# ---------------------------------------------------------------------
@login_required
def cliente_actualizar(request):
    if request.method == "POST":
        cliente_id = request.POST.get("cliente_id")
        cliente = get_object_or_404(Cliente, pk=cliente_id)
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
    return redirect("clientes")


# ---------------------------------------------------------------------
# ELIMINAR CLIENTE
# ---------------------------------------------------------------------
@login_required
def cliente_eliminar(request):
    if request.method == "POST":
        cliente_id = request.POST.get("cliente_id")
        cliente = get_object_or_404(Cliente, pk=cliente_id)
        cliente.delete()
    return redirect("clientes")

# ---------------------------------------------------------------------
# LISTAR ÓRDENES
# ---------------------------------------------------------------------


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def order_list(request):
    orders = Order.objects.select_related('cliente').prefetch_related(
        'orderdetail_set__menu').order_by('-fecha_registro')

    # Calcular el precio total
    for order in orders:
        order.total_precio = sum(
            float(detail.menu.precio) * detail.cantidad
            for detail in order.orderdetail_set.all()
        )

    order_form = OrderForm()
    order_detail_form = OrderDetailForm()
    clientes = Cliente.objects.all().order_by('nombre')
    menus = Menu.objects.all().order_by('nombre')

    return render(request, 'orders.html', {
        'orders': orders,
        'order_form': order_form,
        'order_detail_form': order_detail_form,
        'clientes': clientes,
        'menus': menus,
    })

# ---------------------------------------------------------------------
# BUSCAR ÓRDENES POR CLIENTE
# ---------------------------------------------------------------------


@login_required
def order_buscar(request):
    if request.method == "POST":
        cliente_id = request.POST.get("cliente")
        orders = Order.objects.select_related('cliente').prefetch_related(
            'orderdetail_set__menu').order_by('-fecha_registro')
        if cliente_id != "todos":
            orders = orders.filter(cliente_id=cliente_id)

        # Calcular precio total
        for order in orders:
            order.total_precio = sum(
                float(detail.menu.precio) * detail.cantidad
                for detail in order.orderdetail_set.all()
            )
    else:
        return redirect("orders")

    order_form = OrderForm()
    order_detail_form = OrderDetailForm()
    clientes = Cliente.objects.all().order_by('nombre')
    menus = Menu.objects.all().order_by('nombre')

    return render(request, 'orders.html', {
        'orders': orders,
        'order_form': order_form,
        'order_detail_form': order_detail_form,
        'clientes': clientes,
        'menus': menus,
    })

# ---------------------------------------------------------------------
# AGREGAR ÓRDEN
# ---------------------------------------------------------------------


@login_required
def order_agregar(request):
    if request.method == "POST":
        order_form = OrderForm(request.POST)
        if order_form.is_valid():
            order = order_form.save()
            # Guardar detalles del pedido
            for menu_id, cantidad in zip(request.POST.getlist('menu'), request.POST.getlist('cantidad')):
                OrderDetail.objects.create(
                    order=order, menu_id=menu_id, cantidad=cantidad)
    return redirect("orders")

# ---------------------------------------------------------------------
# ACTUALIZAR ÓRDEN
# ---------------------------------------------------------------------


@login_required
def order_actualizar(request):
    if request.method == "POST":
        order_id = request.POST.get("order_id")
        order = get_object_or_404(Order, pk=order_id)
        order_form = OrderForm(request.POST, instance=order)
        if order_form.is_valid():
            order = order_form.save()
            # Actualizar detalles
            OrderDetail.objects.filter(order=order).delete()
            for menu_id, cantidad in zip(request.POST.getlist('menu'), request.POST.getlist('cantidad')):
                OrderDetail.objects.create(
                    order=order, menu_id=menu_id, cantidad=cantidad)
    return redirect("orders")

# ---------------------------------------------------------------------
# ELIMINAR ÓRDEN
# ---------------------------------------------------------------------


@login_required
def order_eliminar(request):
    if request.method == "POST":
        order_id = request.POST.get("order_id")
        order = get_object_or_404(Order, pk=order_id)
        order.delete()
    return redirect("orders")


# Clase personalizada para definir el título del PDF


class MyDocTemplate(SimpleDocTemplate):
    def __init__(self, *args, pdf_title=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.pdf_title = pdf_title

    def build(self, flowables, onFirstPage=None, onLaterPages=None, canvasmaker=canvas.Canvas):
        # Intercepta la creación del canvas para asignar el título
        def set_pdf_title(c, doc):
            if self.pdf_title:
                c.setTitle(self.pdf_title)
        super().build(flowables, onFirstPage=set_pdf_title,
                      onLaterPages=set_pdf_title, canvasmaker=canvasmaker)


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def create_invoice(request, order_id):
    # Obtener configuración del sistema
    config = SystemConfig.get_config()

    # Optimizar consulta con select_related y prefetch_related
    order = get_object_or_404(
        Order.objects.select_related(
            'cliente').prefetch_related('orderdetail_set__menu'),
        pk=order_id
    )

    fecha_registro_formateada = order.fecha_registro.strftime(
        "%Y-%m-%d %I:%M %p")

    # Sanitizar nombre de archivo
    nombre_cliente = str(order.cliente).replace('/', '_').replace('\\', '_')
    fecha_archivo = fecha_registro_formateada.replace(
        ' ', '_').replace(':', '-')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Factura_{order_id}_{nombre_cliente}_{fecha_archivo}.pdf"'

    # Crear PDF tamaño carta con márgenes optimizados
    pdf_title = f'Factura #{order_id} - {order.cliente.nombre}'
    doc = MyDocTemplate(
        response,
        pagesize=letter,
        rightMargin=0.70 * inch,
        leftMargin=0.70 * inch,
        topMargin=0.20 * inch,
        bottomMargin=0.20 * inch,
        pdf_title=pdf_title
    )

    elements = []
    styles = getSampleStyleSheet()

    # ================= ESTILOS =================
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#7f8c8d'),
        alignment=TA_CENTER,
        spaceAfter=10
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=8,
        fontName='Helvetica-Bold'
    )

    info_label_style = ParagraphStyle(
        'InfoLabel',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#7f8c8d'),
        fontName='Helvetica-Bold'
    )

    info_value_style = ParagraphStyle(
        'InfoValue',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#2c3e50')
    )

    total_style = ParagraphStyle(
        'TotalStyle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#27ae60'),
        fontName='Helvetica-Bold',
        alignment=TA_RIGHT
    )

    # ============ ENCABEZADO ============
    elements.append(Paragraph('FACTURA', title_style))
    elements.append(Paragraph(f'Pedido #{order_id}', subtitle_style))

    # Información del restaurante
    if config.restaurant_name:
        restaurant_info_style = ParagraphStyle(
            'RestaurantInfo',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#7f8c8d'),
            alignment=TA_CENTER
        )
        elements.append(
            Paragraph(config.restaurant_name, restaurant_info_style))

        if config.restaurant_address:
            elements.append(
                Paragraph(config.restaurant_address, restaurant_info_style))

        if config.restaurant_phone or config.restaurant_email:
            contact_info = []
            if config.restaurant_phone:
                contact_info.append(f'Tel: {config.restaurant_phone}')
            if config.restaurant_email:
                contact_info.append(f'Email: {config.restaurant_email}')

            elements.append(Paragraph(' | '.join(
                contact_info), restaurant_info_style))

    elements.append(Spacer(1, 8))

    elements.append(HRFlowable(
        width="100%",
        thickness=2,
        color=colors.HexColor('#3498db'),
        spaceAfter=8
    ))

    # ============ INFORMACIÓN DEL CLIENTE ============
    elements.append(Paragraph('Información del Cliente', heading_style))

    client_data = [
        [
            Paragraph('Cliente:', info_label_style),
            Paragraph(order.cliente.nombre, info_value_style),
            Paragraph('Fecha:', info_label_style),
            Paragraph(fecha_registro_formateada, info_value_style)
        ]
    ]

    client_table = Table(client_data, colWidths=[
                         0.9 * inch, 2.2 * inch, 0.9 * inch, 2.0 * inch])
    client_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4)
    ]))

    elements.append(client_table)
    elements.append(Spacer(1, 6))

    # ============ DETALLES DEL PEDIDO ============
    elements.append(Paragraph('Detalles del Pedido', heading_style))
    elements.append(Spacer(1, 4))

    data = [['Platillo', 'Cantidad', 'Precio Unit.', 'Total']]
    subtotal = 0

    for detail in order.orderdetail_set.all():
        precio_unitario = float(detail.menu.precio)
        precio_total = precio_unitario * detail.cantidad
        subtotal += precio_total

        data.append([
            detail.menu.nombre,
            str(detail.cantidad),
            f'RD$ {precio_unitario:.2f}',
            f'RD$ {precio_total:.2f}'
        ])

    # ========= TABLA OPTIMIZADA PARA EVITAR SALTOS =========
    table = LongTable(
        data,
        colWidths=[2.5 * inch, 0.9 * inch, 1.1 * inch, 1.1 * inch],
        repeatRows=1
    )

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),

        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 3),

        ('ROWBACKGROUNDS', (0, 1), (-1, -1),
         [colors.white, colors.HexColor('#ecf0f1')]),

        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#bdc3c7')),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 10))

    # ============ RESUMEN DE TOTALES ============
    itbis = subtotal * (float(config.itbis_rate) / 100)
    total_con_itbis = subtotal + itbis

    propina = 0
    if config.show_tip_in_invoice:
        propina = total_con_itbis * (float(config.suggested_tip_rate) / 100)

    total_final = total_con_itbis + propina

    summary_data = [
        [Paragraph('Subtotal:', info_label_style), Paragraph(
            f'RD$ {subtotal:.2f}', info_value_style)],
        [Paragraph(f'ITBIS ({config.itbis_rate}%):', info_label_style), Paragraph(
            f'RD$ {itbis:.2f}', info_value_style)]
    ]

    if config.show_tip_in_invoice:
        summary_data.append([
            Paragraph(
                f'Propina sugerida ({config.suggested_tip_rate}%):', info_label_style),
            Paragraph(f'RD$ {propina:.2f}', info_value_style)
        ])

    summary_table = Table(summary_data, colWidths=[4.2 * inch, 1.6 * inch])
    summary_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4)
    ]))

    elements.append(summary_table)
    elements.append(Spacer(1, 8))

    # ============ TOTAL FINAL ============
    elements.append(HRFlowable(
        width="100%",
        thickness=1,
        color=colors.HexColor('#bdc3c7'),
        spaceAfter=10
    ))

    total_table = Table(
        [[Paragraph('TOTAL A PAGAR:', total_style), Paragraph(
            f'RD$ {total_final:.2f}', total_style)]],
        colWidths=[3.3 * inch, 2.5 * inch]
    )

    total_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (1, 0), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e8f8f5')),
        ('BOX', (0, 0), (-1, -1), 1.2, colors.HexColor('#27ae60'))
    ]))

    elements.append(total_table)
    elements.append(Spacer(1, 10))

    # ============ PIE DE PÁGINA ============
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#95a5a6'),
        alignment=TA_CENTER
    )

    elements.append(HRFlowable(
        width="100%",
        thickness=1,
        color=colors.HexColor('#bdc3c7'),
        spaceBefore=6,
        spaceAfter=6
    ))

    if config.invoice_footer_message:
        elements.append(Paragraph(config.invoice_footer_message, footer_style))

    elements.append(Paragraph(
        config.restaurant_name or 'Sistema de Restaurante ADM',
        footer_style
    ))

    # Construir PDF
    doc.build(elements)
    return response


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def logout_view(request):
    auth_logout(request)
    messages.success(request, 'Has cerrado sesión correctamente')
    return redirect('login')

# ---------------------------------------------------------------------
# LISTAR PLATILLOS
# ---------------------------------------------------------------------


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def menu_list(request):
    dishes = Menu.objects.all().order_by("id")
    form = MenuForm()
    return render(request, "menu.html", {
        "dishes": dishes,
        "form": form,
    })

# ---------------------------------------------------------------------
# BUSCAR PLATILLOS
# ---------------------------------------------------------------------


@login_required
def menu_buscar(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre", "")
        dishes = Menu.objects.filter(nombre__icontains=nombre)
    else:
        return redirect("menu")

    form = MenuForm()
    return render(request, "menu.html", {
        "dishes": dishes,
        "form": form,
    })

# ---------------------------------------------------------------------
# AGREGAR PLATILLO
# ---------------------------------------------------------------------


@login_required
def menu_agregar(request):
    if request.method == "POST":
        form = MenuForm(request.POST)
        if form.is_valid():
            form.save()
    return redirect("menu")

# ---------------------------------------------------------------------
# ACTUALIZAR PLATILLO
# ---------------------------------------------------------------------


@login_required
def menu_actualizar(request):
    if request.method == "POST":
        dish_id = request.POST.get("dish_id")
        dish = get_object_or_404(Menu, pk=dish_id)
        form = MenuForm(request.POST, instance=dish)
        if form.is_valid():
            form.save()
    return redirect("menu")

# ---------------------------------------------------------------------
# ELIMINAR PLATILLO
# ---------------------------------------------------------------------


@login_required
def menu_eliminar(request):
    if request.method == "POST":
        dish_id = request.POST.get("dish_id")
        dish = get_object_or_404(Menu, pk=dish_id)
        dish.delete()
    return redirect("menu")
