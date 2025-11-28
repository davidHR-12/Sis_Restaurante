"""
URL configuration for Sis_Restaurante project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from Web_Restaurante import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # LOGIN / LOGOUT
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # HOME
    path('home/', views.home, name='home'),

    # CLIENTES (CRUD DIVIDIDO)
    path('home/client/', views.cliente_list, name='clientes'),
    path('home/client/buscar/', views.cliente_buscar, name='cliente_buscar'),
    path('home/client/agregar/', views.cliente_agregar, name='cliente_agregar'),
    path('home/client/actualizar/', views.cliente_actualizar, name='cliente_actualizar'),
    path('home/client/eliminar/', views.cliente_eliminar, name='cliente_eliminar'),

    # ÓRDENES
    path('orders/', views.order_list, name='orders'),
    path('orders/buscar/', views.order_buscar, name='order_buscar'),
    path('orders/agregar/', views.order_agregar, name='order_agregar'),
    path('orders/actualizar/', views.order_actualizar, name='order_actualizar'),
    path('orders/eliminar/', views.order_eliminar, name='order_eliminar'),
    path('orders/factura/<int:order_id>/', views.create_invoice, name='create_invoice'),

    # MENÚ
    path('menu/', views.menu_list, name='menu'),
    path('menu/buscar/', views.menu_buscar, name='menu_buscar'),
    path('menu/agregar/', views.menu_agregar, name='menu_agregar'),
    path('menu/actualizar/', views.menu_actualizar, name='menu_actualizar'),
    path('menu/eliminar/', views.menu_eliminar, name='menu_eliminar'),
]
