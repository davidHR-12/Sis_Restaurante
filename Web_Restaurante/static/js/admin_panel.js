// Tab switching functionality
document.addEventListener('DOMContentLoaded', function() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetTab = button.getAttribute('data-tab');
            
            // Remove active class from all buttons and contents
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active class to clicked button and corresponding content
            button.classList.add('active');
            const targetContent = document.getElementById(`tab-${targetTab}`);
            if (targetContent) {
                targetContent.classList.add('active');
            }
            
            // Update URL without reload
            const url = new URL(window.location);
            url.searchParams.set('tab', targetTab);
            window.history.pushState({}, '', url);
        });
    });
    
    // Activate tab from URL parameter
    const urlParams = new URLSearchParams(window.location.search);
    const activeTab = urlParams.get('tab') || 'dashboard';
    const activeButton = document.querySelector(`[data-tab="${activeTab}"]`);
    if (activeButton) {
        activeButton.click();
    }
});

// ========== FUNCIONES PARA GESTIÓN DE USUARIOS ==========

// Abrir modal de crear usuario
function openCreateUserModal() {
    const modal = document.getElementById('createUserModal');
    modal.classList.remove('hidden');
    modal.classList.add('flex');
}

// Cerrar modal de crear usuario
function closeCreateUserModal() {
    const modal = document.getElementById('createUserModal');
    modal.classList.add('hidden');
    modal.classList.remove('flex');
}

// Abrir modal de editar usuario
function openEditUserModal(id, username, email, isSuperuser, isActive) {
    document.getElementById('edit_user_id').value = id;
    document.getElementById('edit_username').value = username;
    document.getElementById('edit_email').value = email || '';
    document.getElementById('edit_is_superuser').checked = isSuperuser;
    document.getElementById('edit_is_active').checked = isActive;
    
    const modal = document.getElementById('editUserModal');
    modal.classList.remove('hidden');
    modal.classList.add('flex');
}

// Cerrar modal de editar usuario
function closeEditUserModal() {
    const modal = document.getElementById('editUserModal');
    modal.classList.add('hidden');
    modal.classList.remove('flex');
}

// Abrir modal de eliminar usuario
function openDeleteUserModal(id, username) {
    document.getElementById('delete_user_id').value = id;
    document.getElementById('delete_username').textContent = username;
    
    const modal = document.getElementById('deleteUserModal');
    modal.classList.remove('hidden');
    modal.classList.add('flex');
}

// Cerrar modal de eliminar usuario
function closeDeleteUserModal() {
    const modal = document.getElementById('deleteUserModal');
    modal.classList.add('hidden');
    modal.classList.remove('flex');
}

// Cerrar modales al hacer clic fuera de ellos
document.addEventListener('click', function(e) {
    const createModal = document.getElementById('createUserModal');
    const editModal = document.getElementById('editUserModal');
    const deleteModal = document.getElementById('deleteUserModal');
    
    if (e.target === createModal) {
        closeCreateUserModal();
    }
    if (e.target === editModal) {
        closeEditUserModal();
    }
    if (e.target === deleteModal) {
        closeDeleteUserModal();
    }
});

// Cerrar modales con la tecla Escape
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeCreateUserModal();
        closeEditUserModal();
        closeDeleteUserModal();
    }
});

// Hacer las funciones globales
window.openCreateUserModal = openCreateUserModal;
window.closeCreateUserModal = closeCreateUserModal;
window.openEditUserModal = openEditUserModal;
window.closeEditUserModal = closeEditUserModal;
window.openDeleteUserModal = openDeleteUserModal;
window.closeDeleteUserModal = closeDeleteUserModal;