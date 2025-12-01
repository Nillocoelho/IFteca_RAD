// Inicializa os ícones Lucide
lucide.createIcons();

// Recupera dados da reserva do sessionStorage
document.addEventListener('DOMContentLoaded', function() {
    const reservaData = sessionStorage.getItem('ultimaReserva');
    
    if (reservaData) {
        try {
            const reserva = JSON.parse(reservaData);
            
            // Preenche os dados na tela
            document.getElementById('salaNome').textContent = reserva.sala.nome;
            document.getElementById('salaLocalizacao').textContent = reserva.sala.localizacao || '1º Andar - Bloco A';
            document.getElementById('reservaData').textContent = reserva.data;
            document.getElementById('reservaHorario').textContent = reserva.horario;
            
            // Limpa o sessionStorage para evitar reutilização
            sessionStorage.removeItem('ultimaReserva');
        } catch (e) {
            console.error('Erro ao processar dados da reserva:', e);
        }
    }
});
