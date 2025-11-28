from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Cliente, Menu, OrderDetail, Order
from .forms import ClienteForm, BuscarClienteForm, MenuForm, BuscarMenuForm, OrderForm, OrderDetailForm, BuscarOrderForm

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
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
                messages.error(request, 'El usuario o contraseña es incorrecto')
        else:
            messages.error(request, 'Por favor, complete todos los campos')
    return render(request, 'login.html')

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def home(request):
    return render(request, 'home.html')

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
    orders = Order.objects.select_related('cliente').prefetch_related('orderdetail_set__menu').order_by('-fecha_registro')

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
        orders = Order.objects.select_related('cliente').prefetch_related('orderdetail_set__menu').order_by('-fecha_registro')
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
                OrderDetail.objects.create(order=order, menu_id=menu_id, cantidad=cantidad)
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
                OrderDetail.objects.create(order=order, menu_id=menu_id, cantidad=cantidad)
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


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def create_invoice(request, order_id):
    # Optimizar consulta con select_related y prefetch_related
    order = get_object_or_404(
        Order.objects.select_related('cliente').prefetch_related('orderdetail_set__menu'),
        pk=order_id
    )
    
    fecha_registro_formateada = order.fecha_registro.strftime("%Y-%m-%d %I:%M %p")
    
    # Sanitizar nombre de archivo
    nombre_cliente = str(order.cliente).replace('/', '_').replace('\\', '_')
    fecha_archivo = fecha_registro_formateada.replace(' ', '_').replace(':', '-')
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Factura_{order_id}_{nombre_cliente}_{fecha_archivo}.pdf"'

    # Crear PDF con tamaño carta y márgenes personalizados
    doc = SimpleDocTemplate(
        response,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#7f8c8d'),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=12,
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
        fontSize=14,
        textColor=colors.HexColor('#27ae60'),
        fontName='Helvetica-Bold',
        alignment=TA_RIGHT
    )

    # ====== ENCABEZADO ======
    elements.append(Paragraph('FACTURA', title_style))
    elements.append(Paragraph(f'Pedido #{order_id}', subtitle_style))
    elements.append(Spacer(1, 20))

    # Línea decorativa
    elements.append(HRFlowable(
        width="100%",
        thickness=2,
        color=colors.HexColor('#3498db'),
        spaceAfter=20
    ))

    # ====== INFORMACIÓN DEL CLIENTE ======
    elements.append(Paragraph('Información del Cliente', heading_style))
    
    # Tabla de información del cliente
    client_data = [
        [Paragraph('Cliente:', info_label_style), 
         Paragraph(order.cliente.nombre, info_value_style)],
        [Paragraph('Fecha:', info_label_style), 
         Paragraph(fecha_registro_formateada, info_value_style)]
    ]
    
    client_table = Table(client_data, colWidths=[1.5*inch, 4*inch])
    client_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    elements.append(client_table)
    elements.append(Spacer(1, 25))

    # ====== DETALLES DEL PEDIDO ======
    elements.append(Paragraph('Detalles del Pedido', heading_style))
    elements.append(Spacer(1, 12))

    # Datos de la tabla con encabezados
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
    
    # Calcular impuestos (ITBIS 18% en República Dominicana)
    itbis_rate = 0.18
    itbis = subtotal * itbis_rate
    total_precio = subtotal + itbis

    # Crear tabla de productos
    table = Table(data, colWidths=[3*inch, 1*inch, 1.2*inch, 1.3*inch])
    table.setStyle(TableStyle([
        # Estilo del encabezado
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Estilo del cuerpo
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#2c3e50')),
        
        # Filas alternadas
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecf0f1')]),
        
        # Bordes
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
        ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor('#3498db')),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 20))

    # ====== RESUMEN DE TOTALES ======
    summary_label_style = ParagraphStyle(
        'SummaryLabel',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#2c3e50'),
        fontName='Helvetica'
    )
    
    summary_value_style = ParagraphStyle(
        'SummaryValue',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#2c3e50'),
        fontName='Helvetica'
    )
    
    # Tabla de resumen (Subtotal, ITBIS, Total)
    summary_data = [
        [Paragraph('Subtotal:', summary_label_style), 
         Paragraph(f'RD$ {subtotal:.2f}', summary_value_style)],
        [Paragraph('ITBIS (18%):', summary_label_style), 
         Paragraph(f'RD$ {itbis:.2f}', summary_value_style)]
    ]
    
    summary_table = Table(summary_data, colWidths=[4.5*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 10))

    # ====== TOTAL ======
    # Línea decorativa antes del total
    elements.append(HRFlowable(
        width="100%",
        thickness=1,
        color=colors.HexColor('#bdc3c7'),
        spaceAfter=15
    ))
    
    # Tabla para el total
    total_data = [[
        Paragraph('TOTAL A PAGAR:', total_style),
        Paragraph(f'RD$ {total_precio:.2f}', total_style)
    ]]
    
    total_table = Table(total_data, colWidths=[4.5*inch, 2*inch])
    total_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'RIGHT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e8f8f5')),
        ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor('#27ae60')),
    ]))
    
    elements.append(total_table)
    elements.append(Spacer(1, 30))

    # ====== PIE DE PÁGINA ======
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#95a5a6'),
        alignment=TA_CENTER
    )
    
    elements.append(Spacer(1, 20))
    elements.append(HRFlowable(
        width="100%",
        thickness=1,
        color=colors.HexColor('#bdc3c7'),
        spaceBefore=10,
        spaceAfter=10
    ))
    elements.append(Paragraph('Gracias por su preferencia', footer_style))
    elements.append(Paragraph('Sistema de Restaurante ADM', footer_style))

    # Construir el PDF
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