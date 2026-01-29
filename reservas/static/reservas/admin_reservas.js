let reservaParaCancelar = null;

document.addEventListener('click', function(e){
  if(e.target.closest('.btn-cancel')){
    const btn = e.target.closest('.btn-cancel');
    reservaParaCancelar = btn.getAttribute('data-id');
    
    // Atualiza o texto do modal com informações da linha
    const row = btn.closest('tr');
    const usuario = row.cells[0].querySelector('.fw-semibold').textContent;
    const sala = row.cells[1].textContent.trim();
    const data = row.cells[2].textContent.trim();
    const horario = row.cells[3].textContent;
    
    const modalTexto = document.getElementById('modalTexto');
    modalTexto.innerHTML = `Você está prestes a cancelar a reserva de <strong>${usuario}</strong> para a <strong>${sala}</strong> no dia <strong>${data}</strong> das <strong>${horario}</strong>. Esta ação não pode ser desfeita.`;
    
    // Abre o modal
    const modal = new bootstrap.Modal(document.getElementById('modalCancelar'));
    modal.show();
  }
});

document.getElementById('btnConfirmarCancelar').addEventListener('click', function(){
  if(!reservaParaCancelar) return;

  const csrf = getCsrfToken();
  if(!csrf){
    // tenta obter do input oculto (fallback caso o cookie ainda não exista)
    const hidden = document.querySelector('#csrfBootstrap input[name=\"csrfmiddlewaretoken\"]');
    if (hidden) {
      document.cookie = `csrftoken=${hidden.value}; path=/`;
    }
  }

  const csrfToken = getCsrfToken();
  if(!csrfToken){
    alert('Token CSRF não encontrado. Recarregue a página e tente novamente.');
    return;
  }

  fetch(`/reservas/admin/reservas/${reservaParaCancelar}/cancelar/`, {
    method: 'POST',
    headers: {
      'Accept': 'application/json',
      'X-Requested-With': 'XMLHttpRequest',
      'X-CSRFToken': csrfToken,
      'Content-Type': 'application/json'
    },
    credentials: 'same-origin'
  })
  .then(async (r)=>{
    const contentType = r.headers.get('content-type') || '';
    if(!r.ok){
      const body = contentType.includes('application/json') ? await r.json() : await r.text();
      const msg = (body && body.error) || (body && body.detail) || r.statusText || 'Erro ao cancelar';
      throw new Error(msg);
    }
    return contentType.includes('application/json') ? r.json() : {};
  })
  .then(j=>{
    if(j.success){
      // Fecha o modal
      const modal = bootstrap.Modal.getInstance(document.getElementById('modalCancelar'));
      modal.hide();
      
      // Atualiza a linha da tabela
      const btn = document.querySelector(`.btn-cancel[data-id="${reservaParaCancelar}"]`);
      if(btn){
        const row = btn.closest('tr');
        row.cells[4].innerHTML = '<span class="badge bg-danger">Cancelada</span>';
        btn.remove();
      }
      
      reservaParaCancelar = null;
      showNotification('Reserva cancelada com sucesso.', 'success');
    } else {
      const msg = j.error || j.message || 'Erro ao cancelar';
      showNotification(msg, 'error');
      alert(msg);
    }
  }).catch(err=>{
    console.error(err);
    const msg = err.message || 'Erro ao comunicar com o servidor.';
    showNotification(msg, 'error');
    alert(msg);
  });
});

// Obtém o token CSRF do cookie (necessário para POST via fetch)
function getCsrfToken(name = 'csrftoken') {
  const cookies = document.cookie ? document.cookie.split('; ') : [];
  for (const cookie of cookies) {
    const [key, value] = cookie.split('=');
    if (key === name) return decodeURIComponent(value);
  }
  return null;
}

// Toast simples no canto inferior direito
function showNotification(message, type = 'info') {
  const existing = document.querySelector('.toast-notification');
  if (existing) existing.remove();

  const toast = document.createElement('div');
  toast.className = `toast-notification toast-${type}`;
  toast.innerHTML = `
    <i class="bi ${type === 'success' ? 'bi-check-circle' : 'bi-info-circle'}"></i>
    <span>${message}</span>
  `;

  toast.style.cssText = `
    position: fixed;
    bottom: 20px;
    left: 50%;
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 14px 18px;
    background: ${type === 'success' ? '#008B45' : '#dc3545'};
    color: white;
    border-radius: 10px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.2);
    font-size: 14px;
    font-weight: 600;
    z-index: 9999;
    transform: translateX(-50%);
    animation: slideIn 0.25s ease;
  `;

  const style = document.createElement('style');
  style.textContent = `
    @keyframes slideIn {
      from { transform: translate(-50%, 20px); opacity: 0; }
      to { transform: translate(-50%, 0); opacity: 1; }
    }
  `;
  document.head.appendChild(style);

  document.body.appendChild(toast);
  setTimeout(() => {
    toast.style.animation = 'slideIn 0.25s ease reverse';
    setTimeout(() => toast.remove(), 250);
  }, 3500);
}

