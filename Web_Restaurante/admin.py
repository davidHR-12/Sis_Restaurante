from django.contrib import admin
from .models import Cliente

admin.site.site_header = "Gestión Restaurante"  # Título de la barra superior
admin.site.site_title = "Panel Admin"          # Título de la página
admin.site.index_title = "Bienvenido al Panel Administrativo"



@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'correo', 'telefono')  # Columnas visibles
    search_fields = ('nombre', 'correo')             # Barra de búsqueda