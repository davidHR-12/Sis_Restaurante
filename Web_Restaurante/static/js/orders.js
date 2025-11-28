// Datos de menús (se pueden pasar desde Django como JSON en el HTML)
let menus = [];

// Función para llenar el formulario con datos del pedido
// Debe estar definida ANTES de DOMContentLoaded para que onclick funcione
window.fillOrderForm = function(id, cliente_id, estado, details) {
    document.getElementById('order_id').value = id;
    document.getElementById('order_cliente').value = cliente_id;
    document.getElementById('order_estado').value = estado;
    
    const platillosDiv = document.getElementById('order-platillos');
    platillosDiv.innerHTML = '';

    details.forEach(detail => {
        const newPlatillo = document.createElement('div');
        newPlatillo.className = 'order-platillo flex items-center space-x-2';
        newPlatillo.innerHTML = `
            <select name="menu" class="menu-select flex-1 px-3 py-2 bg-input border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent transition-all duration-200 text-foreground text-sm">
                ${menus.map(menu => `<option value="${menu.id}" ${menu.id == detail.menu_id ? 'selected' : ''}>${menu.nombre}</option>`).join('')}
            </select>
            <input type="number" name="cantidad" min="1" value="${detail.cantidad}" class="menu-cantidad w-20 px-3 py-2 bg-input border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent transition-all duration-200 text-foreground text-sm">
            <button type="button" class="remove-platillo bg-destructive hover:bg-destructive/90 text-destructive-foreground w-8 h-8 rounded-lg transition-all duration-200 flex items-center justify-center">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            </button>
        `;
        platillosDiv.appendChild(newPlatillo);
    });
};

// Función para ir a la página de factura
window.goToInvoice = function() {
    const orderId = document.getElementById('order_id').value;
    if (orderId) {
        window.open(`/orders/factura/${orderId}/`, '_blank');
    } else {
        alert("Seleccione un pedido para crear la factura.");
    }
};

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Cargar datos de menús desde la variable global
    if (typeof window.menusData !== 'undefined') {
        menus = window.menusData;
    }
    document.getElementById('add-platillo').addEventListener('click', function() {
        const platillosDiv = document.getElementById('order-platillos');
        const newPlatillo = platillosDiv.children[0].cloneNode(true);
        newPlatillo.querySelector('input[name="cantidad"]').value = 1;
        platillosDiv.appendChild(newPlatillo);
    });
    
    // Event listener para cambio de cliente
document.addEventListener('click', function(e) {
    if (e.target && e.target.classList.contains('remove-platillo')) {
        const platillosDiv = document.getElementById('order-platillos');
        if (platillosDiv.children.length > 1) {
            e.target.closest('.order-platillo').remove();
        } else {
            alert("No se puede eliminar el último platillo.");
        }
    }
});

    // Event listener para cambio de cliente
    document.getElementById('order_cliente').addEventListener('change', function() {
        const clienteId = this.value;
        if (clienteId === 'todos') {
            window.location.href = '/home/orders/';
        } else {
            // Trigger búsqueda automática
            const form = document.getElementById('order-form');
            const buscarButton = form.querySelector('button[formaction*="order_buscar"]');
            if (buscarButton) {
                buscarButton.click();
            }
        }
    });
});

// Event listener para eliminar platillo (fuera de DOMContentLoaded porque usa delegación)