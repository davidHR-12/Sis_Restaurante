document.addEventListener("DOMContentLoaded", () => {
    const passwordFields = document.querySelectorAll("input[type='password']");

    passwordFields.forEach((field) => {
        // Contenedor relativo si no existe
        const wrapper = document.createElement("div");
        wrapper.classList.add("relative");
        wrapper.style.width = "100%";

        // Insertar wrapper antes del input
        field.parentNode.insertBefore(wrapper, field);
        wrapper.appendChild(field);

        // Crear botón
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className =
            "absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition";

        // SVGs
        btn.innerHTML = `
            <!-- Icono ojo abierto -->
            <svg class="w-5 h-5 eye-open" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M2.458 12C3.732 7.943 7.523 5 12 5c4.477 0 8.268 2.943 9.542 7-1.274 4.057-5.065 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>

            <!-- Icono ojo cerrado -->
            <svg class="w-5 h-5 eye-closed hidden" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M3 3l18 18M10.477 10.477a3 3 0 104.243 4.243" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M16.681 16.681C14.88 18.007 13.026 18.75 12 18.75c-4.477 0-8.268-2.943-9.542-7a11.783 11.783 0 012.779-4.476M9.88 9.88a3 3 0 014.243 4.243" />
            </svg>
        `;

        wrapper.appendChild(btn);

        const eyeOpen = btn.querySelector(".eye-open");
        const eyeClosed = btn.querySelector(".eye-closed");

        // Evento para mostrar/ocultar contraseña
        btn.addEventListener("click", () => {
            const isText = field.type === "text";
            field.type = isText ? "password" : "text";

            if (isText) {
                eyeOpen.classList.remove("hidden");
                eyeClosed.classList.add("hidden");
            } else {
                eyeOpen.classList.add("hidden");
                eyeClosed.classList.remove("hidden");
            }
        });
    });
});
