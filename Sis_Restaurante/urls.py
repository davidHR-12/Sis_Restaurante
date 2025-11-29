from django.contrib import admin
from django.urls import path
from Web_Restaurante import views

urlpatterns = [

    # LOGIN / LOGOUT
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # HOME
    path('home/', views.home, name='home'),

    # PANEL DE ADMINISTRACIÓN (Solo Admin)
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/update-config/',
         views.admin_update_config, name='admin_update_config'),
    path('admin-panel/create-user/',
         views.admin_create_user, name='admin_create_user'),
    path('admin-panel/update-user/',
         views.admin_update_user, name='admin_update_user'),
    path('admin-panel/delete-user/',
         views.admin_delete_user, name='admin_delete_user'),
    path('admin-panel/update-profile/',
         views.admin_update_profile, name='admin_update_profile'),
    path('admin-panel/change-password/',
         views.admin_change_password, name='admin_change_password'),

    # CLIENTES (CRUD DIVIDIDO)
    path('home/client/', views.cliente_list, name='clientes'),
    path('home/client/buscar/', views.cliente_buscar, name='cliente_buscar'),
    path('home/client/agregar/', views.cliente_agregar, name='cliente_agregar'),
    path('home/client/actualizar/', views.cliente_actualizar,
         name='cliente_actualizar'),
    path('home/client/eliminar/', views.cliente_eliminar, name='cliente_eliminar'),

    # ÓRDENES
    path('home/orders/', views.order_list, name='orders'),
    path('home/orders/buscar/', views.order_buscar, name='order_buscar'),
    path('home/orders/agregar/', views.order_agregar, name='order_agregar'),
    path('home/orders/actualizar/',
         views.order_actualizar, name='order_actualizar'),
    path('home/orders/eliminar/', views.order_eliminar, name='order_eliminar'),
    path('home/orders/factura/<int:order_id>/',
         views.create_invoice, name='create_invoice'),

    # MENÚ
    path('home/menu/', views.menu_list, name='menu'),
    path('home/menu/buscar/', views.menu_buscar, name='menu_buscar'),
    path('home/menu/agregar/', views.menu_agregar, name='menu_agregar'),
    path('home/menu/actualizar/', views.menu_actualizar, name='menu_actualizar'),
    path('home/menu/eliminar/', views.menu_eliminar, name='menu_eliminar'),
]
