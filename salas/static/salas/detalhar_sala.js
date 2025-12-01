// ========== STATE ==========
let state = {
    currentMonth: new Date().getMonth(),
    currentYear: new Date().getFullYear(),
    selectedDate: new Date(),
    selectedSlot: null,
    availableSlots: []
};

// ========== CSRF TOKEN ==========
function getCsrfToken() {
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : "";
}

// ========== CALENDAR ==========
function renderCalendar() {
    const calendarGrid = document.getElementById("calendarGrid");
    if (!calendarGrid) return;
    
    calendarGrid.innerHTML = "";
    const firstDay = new Date(state.currentYear, state.currentMonth, 1);
    const startDay = firstDay.getDay();
    const daysInMonth = new Date(state.currentYear, state.currentMonth + 1, 0).getDate();

    const monthLabel = document.getElementById("monthLabel");
    if (monthLabel) {
        const monthName = firstDay.toLocaleString("pt-BR", { month: "long" });
        monthLabel.textContent = `${monthName.charAt(0).toUpperCase() + monthName.slice(1)} ${state.currentYear}`;
    }

    // Leading blanks
    for (let i = 0; i < startDay; i++) {
        const div = document.createElement("div");
        div.className = "day muted";
        calendarGrid.appendChild(div);
    }

    // Days
    for (let d = 1; d <= daysInMonth; d++) {
        const dateCell = document.createElement("div");
        dateCell.className = "day";
        dateCell.textContent = d;
        const thisDate = new Date(state.currentYear, state.currentMonth, d);
        
        if (isSameDate(thisDate, state.selectedDate)) {
            dateCell.classList.add("selected");
        }
        
        dateCell.addEventListener("click", () => {
            state.selectedDate = thisDate;
            state.selectedSlot = null;
            renderCalendar();
            loadAvailableSlots();
        });
        
        calendarGrid.appendChild(dateCell);
    }
}

function isSameDate(a, b) {
    return a.getDate() === b.getDate() && 
           a.getMonth() === b.getMonth() && 
           a.getFullYear() === b.getFullYear();
}

// ========== LOAD SLOTS ==========
async function loadAvailableSlots() {
    const slotsList = document.getElementById("slotsList");
    const slotDateLabel = document.getElementById("slotDateLabel");
    
    if (!slotsList) {
        console.error('slotsList element not found');
        return;
    }
    
    // Update date label
    if (slotDateLabel) {
        const dateStr = state.selectedDate.toLocaleDateString("pt-BR", { 
            day: "2-digit", 
            month: "2-digit", 
            year: "numeric" 
        });
        slotDateLabel.textContent = `Horários disponíveis para ${dateStr}:`;
    }
    
    // Show loading
    slotsList.innerHTML = '<div class="text-center text-muted py-4"><i data-lucide="loader"></i><p class="mb-0 mt-2">Carregando horários...</p></div>';
    if (window.lucide) window.lucide.createIcons();
    
    try {
        const dateParam = state.selectedDate.toISOString().split('T')[0];
        const url = `/api/salas/${window.SALA_ID}/horarios/?data=${dateParam}`;
        console.log('Fetching slots from:', url);
        
        const response = await fetch(url);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            console.error('API Error:', response.status, errorData);
            throw new Error(errorData.detail || 'Erro ao carregar horários');
        }
        
        const slots = await response.json();
        console.log('Slots received:', slots);
        
        // Validate response is an array
        if (!Array.isArray(slots)) {
            console.error('API returned non-array:', slots);
            throw new Error('Formato de resposta inválido');
        }
        
        state.availableSlots = slots;
        renderSlots(slots);
        
    } catch (error) {
        console.error('Erro ao carregar horários:', error);
        slotsList.innerHTML = `<div class="text-center text-danger py-4"><p class="mb-0">Erro ao carregar horários: ${error.message}</p></div>`;
    }
}

function renderSlots(slots) {
    const slotsList = document.getElementById("slotsList");
    if (!slotsList) {
        console.error('slotsList element not found');
        return;
    }
    
    // Validate slots is an array
    if (!Array.isArray(slots)) {
        console.error('renderSlots received non-array:', slots);
        slotsList.innerHTML = '<div class="text-center text-danger py-4"><p class="mb-0">Erro ao renderizar horários.</p></div>';
        return;
    }
    
    if (slots.length === 0) {
        slotsList.innerHTML = '<div class="text-center text-muted py-4"><p class="mb-0">Nenhum horário disponível para esta data.</p></div>';
        return;
    }
    
    slotsList.innerHTML = '';
    
    slots.forEach((slot, index) => {
        const slotDiv = document.createElement('div');
        slotDiv.className = `slot ${!slot.disponivel ? 'slot-disabled' : ''}`;
        slotDiv.innerHTML = `
            <span><i data-lucide="clock"></i> ${slot.range}</span>
            ${!slot.disponivel ? '<span class="status-tag">Ocupado</span>' : ''}
        `;
        
        if (slot.disponivel) {
            slotDiv.addEventListener('click', () => selectSlot(slot));
        }
        
        slotsList.appendChild(slotDiv);
    });
    
    if (window.lucide) window.lucide.createIcons();
}

// ========== SELECT SLOT ==========
function selectSlot(slot) {
    state.selectedSlot = slot;
    
    // Update UI
    document.querySelectorAll('.slot').forEach(el => {
        el.classList.remove('slot-selected');
    });
    
    event.currentTarget.classList.add('slot-selected');
    
    // Show summary
    showBookingSummary();
}

function showBookingSummary() {
    const summary = document.getElementById('bookingSummary');
    if (!summary || !state.selectedSlot) return;
    
    const dateStr = state.selectedDate.toLocaleDateString("pt-BR", { 
        day: "2-digit", 
        month: "2-digit", 
        year: "numeric" 
    });
    
    document.getElementById('summaryDate').textContent = dateStr;
    document.getElementById('summaryTime').textContent = state.selectedSlot.range;
    
    summary.style.display = 'block';
    
    // Re-render icons
    if (window.lucide) window.lucide.createIcons();
}

// ========== CONFIRM BOOKING ==========
async function confirmBooking() {
    if (!state.selectedSlot) return;
    
    const btn = document.getElementById('btnConfirmBooking');
    const originalHTML = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<i data-lucide="loader"></i> <span>Processando...</span>';
    if (window.lucide) window.lucide.createIcons();
    
    try {
        const dateParam = state.selectedDate.toISOString().split('T')[0];
        const [inicio, fim] = state.selectedSlot.range.split(' - ');
        
        const response = await fetch('/api/reservas/criar/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({
                sala_id: window.SALA_ID,
                data: dateParam,
                inicio: inicio,
                fim: fim
            })
        });
        
        // Check for authentication errors
        if (response.status === 401 || response.status === 403) {
            alert('Você precisa estar logado para fazer uma reserva. Redirecionando para login...');
            window.location.href = '/login/?next=' + encodeURIComponent(window.location.pathname);
            return;
        }
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Erro ao criar reserva');
        }
        
        // Save reservation data to sessionStorage
        sessionStorage.setItem('ultimaReserva', JSON.stringify(data));
        
        // Redirect to confirmation page
        window.location.href = '/reservas/confirmacao-reserva/';
        
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro ao confirmar reserva: ' + error.message);
        btn.disabled = false;
        btn.innerHTML = originalHTML;
        if (window.lucide) window.lucide.createIcons();
    }
}

// ========== INIT ==========
document.addEventListener("DOMContentLoaded", () => {
    // Calendar navigation
    document.getElementById("prevMonth")?.addEventListener("click", () => {
        state.currentMonth -= 1;
        if (state.currentMonth < 0) {
            state.currentMonth = 11;
            state.currentYear -= 1;
        }
        renderCalendar();
    });

    document.getElementById("nextMonth")?.addEventListener("click", () => {
        state.currentMonth += 1;
        if (state.currentMonth > 11) {
            state.currentMonth = 0;
            state.currentYear += 1;
        }
        renderCalendar();
    });
    
    // Confirm booking button
    document.getElementById("btnConfirmBooking")?.addEventListener("click", confirmBooking);
    
    // Initialize
    if (window.lucide) window.lucide.createIcons();
    renderCalendar();
    loadAvailableSlots();
});
