// Inicializa os ícones Lucide
lucide.createIcons();

// ========== BUSCA DE RESERVAS ==========
const searchInput = document.getElementById('searchReservation');
const reservationCards = document.querySelectorAll('.reservation-card');

if (searchInput) {
    searchInput.addEventListener('input', function(e) {
        const searchTerm = e.target.value.toLowerCase().trim();
        
        reservationCards.forEach(card => {
            const searchData = card.dataset.search.toLowerCase();
            
            if (searchData.includes(searchTerm)) {
                card.style.display = 'flex';
            } else {
                card.style.display = 'none';
            }
        });

        // Verifica se há resultados em cada grupo
        updateEmptyStates(searchTerm);
    });
}

// ========== ATUALIZAR ESTADOS VAZIOS ==========
function updateEmptyStates(searchTerm) {
    const groups = document.querySelectorAll('.reservations-group');
    
    groups.forEach(group => {
        const cards = group.querySelectorAll('.reservation-card');
        const visibleCards = Array.from(cards).filter(card => card.style.display !== 'none');
        const existingEmpty = group.querySelector('.empty-state');
        const existingSearchEmpty = group.querySelector('.search-empty-state');
        
        // Remove estado vazio de busca anterior se existir
        if (existingSearchEmpty) {
            existingSearchEmpty.remove();
        }
        
        if (searchTerm && visibleCards.length === 0) {
            // Oculta estado vazio padrão se existir
            if (existingEmpty) {
                existingEmpty.style.display = 'none';
            }
            
            // Mostra estado vazio de busca
            const list = group.querySelector('.reservations-list');
            const searchEmpty = document.createElement('div');
            searchEmpty.className = 'empty-state search-empty-state';
            searchEmpty.innerHTML = `
                <i data-lucide="search-x"></i>
                <p>Nenhuma reserva encontrada para "${searchTerm}"</p>
            `;
            list.appendChild(searchEmpty);
            lucide.createIcons();
        } else {
            // Restaura estado vazio padrão se necessário
            if (existingEmpty) {
                existingEmpty.style.display = '';
            }
        }
    });
}

// ========== ANIMAÇÃO DE ENTRADA ==========
document.addEventListener('DOMContentLoaded', function() {
    const cards = document.querySelectorAll('.stat-card, .reservation-card');
    
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = 'all 0.4s ease';
            
            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, 50);
        }, index * 50);
    });
});

// ========== ATUALIZAÇÃO AUTOMÁTICA DE CONTADOR ==========
function updateCounters() {
    const reservasAtivasCards = document.querySelectorAll('#reservasAtivasList .reservation-card:not(.empty-state)');
    const reservasAtivasCount = document.getElementById('reservasAtivas');
    
    if (reservasAtivasCount) {
        reservasAtivasCount.textContent = reservasAtivasCards.length;
    }
}

// Atualiza contadores ao carregar
document.addEventListener('DOMContentLoaded', updateCounters);
