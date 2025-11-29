// Función para validar el nombre del platillo (solo letras, números y espacios)
function validateDishName(name) {
  const regex = /^[A-Za-z0-9\s\-&'#áéíóúÁÉÍÓÚ]+$/;
  return regex.test(name);
}

// Función para manejar la entrada en tiempo real
function handleNameInput(event) {
  const input = event.target;
  const name = input.value;

  if (!validateDishName(name)) {
    input.setCustomValidity("El nombre del platillo solo puede contener letras, números y los siguientes caracteres especiales: '-', '&', '#', y ''");
    input.reportValidity();
  } else {
    input.setCustomValidity(""); // Limpiar mensaje de error si es válido
  }
}

// Función para llenar el formulario con los datos del platillo
function fillForm(id, nombre, descripcion, precio) {
    // Validamos el nombre del platillo antes de asignarlo
    if (!validateDishName(nombre)) {
        alert("El nombre del platillo solo puede contener letras, números y los siguientes caracteres especiales: '-', '&', '#', y ''.");
        return; // Salir de la función si el nombre no es válido
    }

    document.getElementById('dish_id').value = id;
    document.getElementById('dish_name').value = nombre;
    document.getElementById('dish_description').value = descripcion;
    document.getElementById('dish_price').value = precio;
}

// Listener para mostrar todos los clientes
document.getElementById('show-all-clients').addEventListener('click', function() {
    window.location.href = '/home/menu/';
});

// Agregar listener para el campo de nombre del platillo en tiempo real
document.getElementById('dish_name').addEventListener('input', handleNameInput);
