from django import forms
from .models import Cliente, Menu, Order, OrderDetail, SystemConfig
import re


class ClienteForm(forms.ModelForm):

    # Validar nombre (prohibir números)
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()

        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', nombre):
            raise forms.ValidationError(
                "El nombre solo puede contener letras y espacios.")

        return nombre

    # Formatear teléfono automáticamente
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono', '')

        # Extraer solo dígitos
        digitos = re.sub(r'\D', '', telefono)

        if len(digitos) == 10:
            # Formato estándar RD → 809-123-4567
            return f"{digitos[0:3]}-{digitos[3:6]}-{digitos[6:10]}"

        elif len(digitos) == 11:
            # Formato internacional → +1-809-123-4567 o similar
            return f"{digitos[0:1]}-{digitos[1:4]}-{digitos[4:7]}-{digitos[7:11]}"

        else:
            raise forms.ValidationError("El número telefónico no es válido.")

    class Meta:
        model = Cliente
        fields = ['nombre', 'telefono', 'correo']


class BuscarClienteForm(forms.Form):
    nombre = forms.CharField(max_length=100, required=False)


class SystemConfigForm(forms.ModelForm):
    class Meta:
        model = SystemConfig
        fields = [
            'restaurant_name',
            'restaurant_address',
            'restaurant_phone',
            'restaurant_email',
            'itbis_rate',
            'invoice_footer_message',
            'suggested_tip_rate',
            'show_tip_in_invoice'
        ]
        widgets = {
            'restaurant_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-input border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent transition-all duration-200 text-gray-100',
                'placeholder': 'Nombre del restaurante'
            }),
            'restaurant_address': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-input border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent transition-all duration-200 text-gray-100',
                'placeholder': 'Dirección completa'
            }),
            'restaurant_phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-input border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent transition-all duration-200 text-gray-100',
                'placeholder': '(809) 555-5555'
            }),
            'restaurant_email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 bg-input border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent transition-all duration-200 text-gray-100',
                'placeholder': 'correo@restaurante.com'
            }),
            'itbis_rate': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 bg-input border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent transition-all duration-200 text-gray-100',
                'placeholder': '18.00',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            'invoice_footer_message': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 bg-input border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent transition-all duration-200 text-gray-100',
                'placeholder': 'Mensaje de agradecimiento',
                'rows': 3
            }),
            'suggested_tip_rate': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 bg-input border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent transition-all duration-200 text-gray-100',
                'placeholder': '10.00',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            'show_tip_in_invoice': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-primary bg-input border-border rounded focus:ring-2 focus:ring-primary'
            })
        }


class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ['nombre', 'descripcion', 'precio']


class BuscarMenuForm(forms.Form):
    nombre = forms.CharField(max_length=100, required=False)


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['cliente', 'estado']


class OrderDetailForm(forms.ModelForm):
    class Meta:
        model = OrderDetail
        fields = ['menu', 'cantidad']


class BuscarOrderForm(forms.Form):
    cliente = forms.CharField(max_length=100, required=False)
