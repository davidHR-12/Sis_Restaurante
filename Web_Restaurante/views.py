from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from .models import Cliente, Menu, OrderDetail, Order
from .forms import ClienteForm, BuscarClienteForm, MenuForm, BuscarMenuForm, OrderForm, OrderDetailForm, BuscarOrderForm

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

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def cliente_view(request):
    buscar_form = BuscarClienteForm(request.GET)
    clientes = Cliente.objects.all().order_by('-fecha_registro')
    form = ClienteForm()
    if request.method == 'POST':
        if 'actualizar' in request.POST:
            cliente_id = request.POST.get('cliente_id')
            if cliente_id:
                cliente = get_object_or_404(Cliente, pk=cliente_id)
                form = ClienteForm(request.POST, instance=cliente)
                if form.is_valid():
                    form.save()
                    return redirect('client')
        elif 'eliminar' in request.POST:
            cliente_id = request.POST.get('cliente_id')
            if cliente_id:
                cliente = get_object_or_404(Cliente, pk=cliente_id)
                cliente.delete()
                return redirect('client')
        elif 'buscar' in request.POST:
            nombre = request.POST.get('nombre')
            if nombre:
                clientes = clientes.filter(nombre__icontains=nombre)
        else:
            form = ClienteForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('client')
    else:
        form = ClienteForm()

    if buscar_form.is_valid():
        nombre = buscar_form.cleaned_data['nombre']
        if nombre:
            clientes = clientes.filter(nombre__icontains=nombre)

    return render(request, 'client.html', {'form': form, 'buscar_form': buscar_form, 'clientes': clientes})

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def order_view(request):
    buscar_form = BuscarOrderForm(request.GET)
    # Optimizar consultas con select_related y prefetch_related
    orders = Order.objects.select_related('cliente').prefetch_related('orderdetail_set__menu').order_by('-fecha_registro')
    order_form = OrderForm()
    order_detail_form = OrderDetailForm()

    # Calcular el precio total para cada pedido (optimizado)
    for order in orders:
        order.total_precio = sum(
            float(detail.menu.precio) * detail.cantidad 
            for detail in order.orderdetail_set.all()
        )

    if request.method == 'POST':
        if 'actualizar' in request.POST:
            order_id = request.POST.get('order_id')
            if order_id:
                order = get_object_or_404(Order, pk=order_id)
                order_form = OrderForm(request.POST, instance=order)
                if order_form.is_valid():
                    order = order_form.save()
                    # Actualizar los detalles del pedido
                    OrderDetail.objects.filter(order=order).delete()
                    for menu_id, cantidad in zip(request.POST.getlist('menu'), request.POST.getlist('cantidad')):
                        OrderDetail.objects.create(order=order, menu_id=menu_id, cantidad=cantidad)
                    return redirect('orders')
        elif 'eliminar' in request.POST:
            order_id = request.POST.get('order_id')
            if order_id:
                order = get_object_or_404(Order, pk=order_id)
                order.delete()
                return redirect('orders')
        elif 'buscar' in request.POST:
            cliente_id = request.POST.get('cliente')
            if cliente_id != 'todos':
                orders = orders.filter(cliente_id=cliente_id)
        else:
            order_form = OrderForm(request.POST)
            if order_form.is_valid():
                order = order_form.save()
                for menu_id, cantidad in zip(request.POST.getlist('menu'), request.POST.getlist('cantidad')):
                    OrderDetail.objects.create(order=order, menu_id=menu_id, cantidad=cantidad)
                return redirect('orders')
    else:
        order_form = OrderForm()

    if buscar_form.is_valid():
        cliente_id = buscar_form.cleaned_data['cliente']
        if cliente_id:
            orders = orders.filter(cliente_id=cliente_id)

    # Optimizar consultas para evitar múltiples queries
    clientes = Cliente.objects.all().order_by('nombre')
    menus = Menu.objects.all().order_by('nombre')

    return render(request, 'orders.html', {
        'order_form': order_form,
        'order_detail_form': order_detail_form,
        'buscar_form': buscar_form,
        'orders': orders,
        'clientes': clientes,
        'menus': menus
    })


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def create_invoice(request, order_id):
    # Optimizar consulta con select_related y prefetch_related
    order = get_object_or_404(
        Order.objects.select_related('cliente').prefetch_related('orderdetail_set__menu'),
        pk=order_id
    )
    fecha_registro_formateada = order.fecha_registro.strftime("%Y-%m-%d %I:%M %p")
    # Sanitizar nombre de archivo para evitar problemas con caracteres especiales
    nombre_cliente = str(order.cliente).replace('/', '_').replace('\\', '_')
    fecha_archivo = fecha_registro_formateada.replace(' ', '_').replace(':', '-')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Factura_{order_id}_{nombre_cliente}_{fecha_archivo}.pdf"'

    # Create the PDF object, using the response object as its "file."
    doc = SimpleDocTemplate(response, pagesize=(400, 400))
    elements = []

    styles = getSampleStyleSheet()
    title_style = styles['Title']
    normal_style = styles['Normal']

    # Title
    elements.append(Paragraph(f'Factura del Pedido {order_id}', title_style))
    elements.append(Spacer(1, 12))

    # Client Info
    elements.append(Paragraph(f'Cliente: {order.cliente.nombre}', normal_style))
    elements.append(Paragraph(f'Fecha de Registro: {fecha_registro_formateada}', normal_style))
    elements.append(Spacer(1, 12))

    # Order Details
    elements.append(Paragraph('Detalles del Pedido:', normal_style))
    elements.append(Spacer(1, 12))

    data = [['Platillo', 'Cantidad', 'Precio Unitario', 'Precio Total']]
    total_precio = 0
    for detail in order.orderdetail_set.all():
        precio_unitario = float(detail.menu.precio)
        precio_total = precio_unitario * detail.cantidad
        total_precio += precio_total
        data.append([
            detail.menu.nombre,
            str(detail.cantidad),
            f'RD ${precio_unitario:.2f}',
            f'RD ${precio_total:.2f}'
        ])

    # Create a table with the data
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.orange),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))

    # Total Price
    elements.append(Paragraph(f'Precio Total: RD ${total_precio:.2f}', normal_style))

    # Build the PDF
    doc.build(elements)
    return response

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def logout_view(request):
    auth_logout(request)
    messages.success(request, 'Has cerrado sesión correctamente')
    return redirect('login')

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def menu_view(request):
    buscar_form = BuscarMenuForm(request.GET)
    dishes = Menu.objects.all().order_by('nombre')
    form = MenuForm()
    if request.method == 'POST':
        if 'actualizar' in request.POST:
            dish_id = request.POST.get('dish_id')
            if dish_id:
                dish = get_object_or_404(Menu, pk=dish_id)
                form = MenuForm(request.POST, instance=dish)
                if form.is_valid():
                    form.save()
                    return redirect('menu')
        elif 'eliminar' in request.POST:
            dish_id = request.POST.get('dish_id')
            if dish_id:
                dish = get_object_or_404(Menu, pk=dish_id)
                dish.delete()
                return redirect('menu')
        elif 'buscar' in request.POST:
            nombre = request.POST.get('nombre')
            if nombre:
                dishes = dishes.filter(nombre__icontains=nombre)
        else:
            form = MenuForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('menu')
    else:
        form = MenuForm()

    if buscar_form.is_valid():
        nombre = buscar_form.cleaned_data['nombre']
        if nombre:
            dishes = dishes.filter(nombre__icontains=nombre)

    return render(request, 'menu.html', {'form': form, 'buscar_form': buscar_form, 'dishes': dishes})