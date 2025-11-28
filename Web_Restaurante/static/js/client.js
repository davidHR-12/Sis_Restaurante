// clientes.js

function fillForm(id, nombre, telefono, correo) {
    document.getElementById("cliente_id").value = id;
    document.getElementById("name_client").value = nombre;
    document.getElementById("tel_client").value = telefono;
    document.getElementById("email_client").value = correo;
}

document.getElementById("show-all-clients").onclick = () => {
    window.location.href = "/home/client/"; // o la URL de tu vista 'clientes'
};

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

document.getElementById("name_client").addEventListener("input", function(e) {
    let valor = e.target.value;
    let limpio = valor.replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]/g, '');
    if (valor !== limpio) {
        e.target.value = limpio;
    }
});
