// clientes.js

// Función para validar el nombre del cliente (solo letras y espacios)
function validateClientName(name) {
    const regex = /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/;
    return regex.test(name);
}

// Función para manejar la entrada en tiempo real
function handleNameInput(event) {
    const input = event.target;
    const name = input.value;

    if (name && !validateClientName(name)) {
        input.setCustomValidity("El nombre solo puede contener letras y espacios");
        input.reportValidity();
    } else {
        input.setCustomValidity(""); // Limpiar mensaje de error si es válido
    }
}

function fillForm(id, nombre, telefono, correo) {
    // Validar el nombre del cliente antes de asignarlo
    if (!validateClientName(nombre)) {
        alert("El nombre solo puede contener letras y espacios");
        return; // Salir de la función si el nombre no es válido
    }

    document.getElementById("cliente_id").value = id;
    document.getElementById("name_client").value = nombre;
    document.getElementById("tel_client").value = telefono;
    document.getElementById("email_client").value = correo;
}

document.getElementById("show-all-clients").onclick = () => {
    window.location.href = "/home/client/";
};

// Formateo automático del teléfono
document.getElementById("tel_client").addEventListener("input", function(e) {
    let valor = e.target.value.replace(/\D/g, "");
    if (valor.length <= 3) {
        e.target.value = valor;
    } else if (valor.length <= 6) {
        e.target.value = valor.slice(0,3) + "-" + valor.slice(3);
    } else if (valor.length <= 10) {
        e.target.value = valor.slice(0,3) + "-" + valor.slice(3,6) + "-" + valor.slice(6);
    } else {
        e.target.value = valor.slice(0,1) + "-" + valor.slice(1,4) + "-" + valor.slice(4,7) + "-" + valor.slice(7,11);
    }
});

// Agregar listener para el campo de nombre del cliente en tiempo real
document.getElementById("name_client").addEventListener("input", handleNameInput);