from django import forms
from .models import Cliente, Menu, Order, OrderDetail

from django import forms
from .models import Cliente, Menu, Order, OrderDetail
import re


class ClienteForm(forms.ModelForm):

    # Validar nombre (prohibir números)
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()

        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', nombre):
            raise forms.ValidationError("El nombre solo puede contener letras y espacios.")

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
 