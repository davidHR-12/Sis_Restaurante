from django.db import models


class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15)
    correo = models.EmailField()
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre


class Menu(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.nombre


class Order(models.Model):
    ESTADO_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('En proceso', 'En proceso'),
        ('Listo', 'Listo'),
        ('Entregado', 'Entregado'),
        ('Cancelado', 'Cancelado'),
    ]
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    platillos = models.ManyToManyField(Menu, through='OrderDetail')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)


class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()


# ========== NUEVO MODELO DE CONFIGURACIÓN ==========
class SystemConfig(models.Model):
    """
    Modelo Singleton para la configuración del sistema.
    Solo debe existir una instancia de este modelo.
    """
    # Información del Restaurante
    restaurant_name = models.CharField(
        max_length=200,
        default='Sistema de Restaurante ADM',
        verbose_name='Nombre del Restaurante'
    )
    restaurant_address = models.CharField(
        max_length=300,
        blank=True,
        verbose_name='Dirección'
    )
    restaurant_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Teléfono'
    )
    restaurant_email = models.EmailField(
        blank=True,
        verbose_name='Email'
    )

    # Configuración de Impuestos
    itbis_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=18.00,
        verbose_name='Tasa de ITBIS (%)',
        help_text='Ingrese el porcentaje sin el símbolo %. Ejemplo: 18.00 para 18%'
    )

    # Configuración de Facturas
    invoice_footer_message = models.TextField(
        default='Gracias por su preferencia',
        verbose_name='Mensaje de pie de página',
        help_text='Mensaje que aparecerá al final de las facturas'
    )

    # Propina sugerida (opcional)
    suggested_tip_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10.00,
        verbose_name='Propina sugerida (%)',
        help_text='Porcentaje de propina sugerida. Ejemplo: 10.00 para 10%'
    )
    show_tip_in_invoice = models.BooleanField(
        default=False,
        verbose_name='Mostrar propina en factura'
    )

    # Metadata
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuración del Sistema'
        verbose_name_plural = 'Configuración del Sistema'

    def __str__(self):
        return f'Configuración del Sistema - {self.restaurant_name}'

    def save(self, *args, **kwargs):
        """
        Asegura que solo exista una instancia de configuración
        """
        if not self.pk and SystemConfig.objects.exists():
            # Si ya existe una configuración, actualizamos esa en lugar de crear una nueva
            existing = SystemConfig.objects.first()
            self.pk = existing.pk
        super().save(*args, **kwargs)

    @classmethod
    def get_config(cls):
        """
        Método helper para obtener la configuración.
        Crea una instancia con valores por defecto si no existe.
        """
        config, created = cls.objects.get_or_create(pk=1)
        return config
