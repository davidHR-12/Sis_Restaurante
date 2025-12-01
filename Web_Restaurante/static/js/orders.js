// Datos de menús (se pueden pasar desde Django como JSON en el HTML)
let menus = [];

// Función para llenar el formulario con datos del pedido (CÓDIGO CORREGIDO)
// Debe estar definida ANTES de DOMContentLoaded para que onclick funcione
window.fillOrderForm = function (id, cliente_id, estado, details) {
  document.getElementById("order_id").value = id;
  document.getElementById("order_cliente").value = cliente_id;
  document.getElementById("order_estado").value = estado;

  const platillosDiv = document.getElementById("order-platillos");
  // 1. Limpiar el contenido anterior
  platillosDiv.innerHTML = "";

  // 2. Recrear los detalles del pedido
  details.forEach((detail) => {
    const newPlatillo = document.createElement("div");
    newPlatillo.className = "order-platillo flex items-center space-x-2";
    newPlatillo.innerHTML = `
            <select name="menu" class="menu-select flex-1 px-3 py-2 bg-input border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent transition-all duration-200 text-gray-100 text-sm">
                ${menus
                  .map(
                    (menu) =>
                      `<option value="${menu.id}" ${
                        menu.id == detail.menu_id ? "selected" : ""
                      }>${menu.nombre}</option>`
                  )
                  .join("")}
            </select>
            <input type="number" name="cantidad" min="1" value="${
              detail.cantidad
            }" class="menu-cantidad w-20 px-3 py-2 bg-input border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent transition-all duration-200 text-gray-100 text-sm">
            <button type="button" class="remove-platillo bg-destructive hover:bg-destructive/90 text-destructive-gray-100 w-8 h-8 rounded-lg transition-all duration-200 flex items-center justify-center">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            </button>
        `;
    platillosDiv.appendChild(newPlatillo);
  });

  // 3. LÓGICA DE HABILITACIÓN/DESHABILITACIÓN REFORZADA
  // Esta lógica se ejecuta después de que los platillos se han añadido al DOM.
  const isEntregado = estado === "Entregado";
  const classNames = [
    "bg-gray-400",
    "text-gray-700",
    "cursor-not-allowed",
  ];

  // Elementos a manipular (seleccionados después de la inserción)
  const formControls = document.querySelectorAll(".menu-select, .menu-cantidad");
  const removeButtons = document.querySelectorAll(".remove-platillo");
  const actionButtons = document.querySelectorAll('button[formaction]');
  const addPlatilloBtn = document.getElementById("add-platillo");
  const clienteSelect = document.getElementById("order_cliente");
  const estadoSelect = document.getElementById("order_estado");
  
// Función centralizada para aplicar/remover estilos y estado
const toggleControls = (disabled) => {
  const disabledClasses = ["bg-gray-400", "text-gray-700", "cursor-not-allowed"];

  // Elementos a manipular
  const elements = [
    clienteSelect,
    estadoSelect,
    addPlatilloBtn,
    ...actionButtons,
    ...formControls,
    ...removeButtons
  ].filter(Boolean);

  elements.forEach(el => {

    // Guardar clases originales una sola vez
    if (!el.dataset.originalClass) {
      el.dataset.originalClass = el.className;
    }

    if (disabled) {
      el.disabled = true;

      // 1. Quitar TODAS las clases de color dinámicas
      el.classList.forEach(cls => {
        if (cls.startsWith("bg-") || cls.startsWith("hover:bg-")) {
          el.classList.remove(cls);
        }
      });

      // 2. Agregar estilo de deshabilitado
      el.classList.add(...disabledClasses);

    } else {

      el.disabled = false;

      // Restaurar clases originales exactas
      el.className = el.dataset.originalClass;

    }
  });
};




  // Aplicar los cambios basándose en el estado del pedido
  toggleControls(isEntregado);
};

// Función para ir a la página de factura
window.goToInvoice = function () {
  const orderId = document.getElementById("order_id").value;
  if (orderId) {
    window.open(`/home/orders/factura/${orderId}/`, "_blank");
  } else {
    alert("Seleccione un pedido para crear la factura.");
  }
};

// Inicializar cuando el DOM esté listo
document.addEventListener("DOMContentLoaded", function () {
  // Cargar datos de menús desde la variable global
  if (typeof window.menusData !== "undefined") {
    menus = window.menusData;
  }
  
  // Listener para agregar platillo
  document
    .getElementById("add-platillo")
    .addEventListener("click", function () {
      const platillosDiv = document.getElementById("order-platillos");
      // Clonar el primer platillo
      const newPlatillo = platillosDiv.children[0].cloneNode(true); 
      newPlatillo.querySelector('input[name="cantidad"]').value = 1;
      
      // Limpiar el estado de "disabled" en el nuevo clon si el botón + está activo
      newPlatillo.querySelectorAll('.menu-select, .menu-cantidad, .remove-platillo').forEach(el => {
        el.disabled = false;
        el.classList.remove('bg-gray-400', 'text-gray-700', 'cursor-not-allowed');
      });
      
      platillosDiv.appendChild(newPlatillo);
    });

  // Event listener para eliminar platillo (delegación de eventos en el documento)
  document.addEventListener("click", function (e) {
    if (e.target && e.target.closest(".remove-platillo")) {
      const btn = e.target.closest(".remove-platillo");
      // Evita que el evento se propague si el botón está deshabilitado
      if (btn.disabled) return; 

      const platillosDiv = document.getElementById("order-platillos");
      if (platillosDiv.children.length > 1) {
        btn.closest(".order-platillo").remove();
      } else {
        alert("No se puede eliminar el último platillo.");
      }
    }
  });

  // Event listener para cambio de cliente (sin cambios)
  document
    .getElementById("order_cliente")
    .addEventListener("change", function () {
      const clienteId = this.value;
      if (clienteId === "todos") {
        window.location.href = "/home/orders/";
      } else {
        // Trigger búsqueda automática
        const form = document.getElementById("order-form");
        const buscarButton = form.querySelector(
          'button[formaction*="order_buscar"]'
        );
        if (buscarButton) {
          buscarButton.click();
        }
      }
    });

});